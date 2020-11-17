<?php
$directory = "../output";
$files = scandir ($directory);
$firstFile = $files[3]; // [0] = '.' ; [1] = '..' ; [2] = '.gitignore'

$str2strip = array("eccs2_", ".log");
$firstDate = str_replace($str2strip, "", $firstFile);

$files = scandir($directory, SCANDIR_SORT_DESCENDING);
$lastFile = $files[0];
$lastDate = str_replace($str2strip, "", $lastFile);

$data = array();
$data['firstDate'] = $firstDate;
$data['lastDate'] = $lastDate;
$data['idp'] = htmlspecialchars($_GET["idp"]);
$data['reg_auth'] = htmlspecialchars($_GET["reg_auth"]);
$data['date'] = htmlspecialchars($_GET["date"]);
$data['status'] = htmlspecialchars($_GET["status"]);
?>

<!DOCTYPE html>
<html>
   <head>
    <meta charset=utf-8 />
    <script type="text/javascript" src="https://code.jquery.com/jquery-3.5.1.js" crossorigin="anonymous"></script>
    <script type="text/javascript" src="https://cdn.datatables.net/1.10.22/js/jquery.dataTables.min.js"></script>
    <link rel="stylesheet" type="text/css" href="https://cdn.datatables.net/1.10.22/css/jquery.dataTables.min.css"/>
    <link href="style.css" rel="stylesheet" type="text/css" />
    <title>eduGAIN Connectivity Check Service 2</title>
  </head>
  <body>
    <hr>
    <div id="status">
      <strong>Show IdPs with status:</strong>
      <input type="checkbox" name="status" value="ERROR">ERROR</input>
      <input type="checkbox" name="status" value="OK">OK</input>
      <input type="checkbox" name="status" value="DISABLED">DISABLED</input>
      <button id="goButton" onclick="getPastResults()">Go</button>
      <input id="myDate" type="date" min="<?php echo $data['firstDate'] ?>" max="<?php echo $data['lastDate'] ?>" value="<?php echo $data['lastDate'] ?>"/>
    </div>
    <hr>
    <button id="btn-show-all-children" type="button">Expand All</button>
    <button id="btn-hide-all-children" type="button">Collapse All</button>
    <hr>
    <div class="container">
      <table id="eccstable" class="cell-border" style="width:100%">
        <thead>
            <tr>
                <th></th>
                <th>DisplayName</th>
                <th>EntityID</th>
                <th>Registration Authority</th>
                <th>Check Date</th>
                <th>Status</th>
            </tr>
        </thead>
      </table>
    </div>
    <script type="text/javascript">
       var date = "<?php echo $data['date'] ?>";
       var reg_auth = "<?php echo $data['reg_auth'] ?>";
       var idp = "<?php echo $data['idp'] ?>";
       var status = "<?php echo $data['status'] ?>";
    </script>
    <script type="text/javascript" src="script.js" /></script>
  </body>
</html>
