<?php
$directory = "../output";
$files = scandir ($directory);
$firstFile = $files[3]; // [0] = '.' ; [1] = '..' ; [2] = '.gitignore'

$str2strip = array("eccs2_", ".log");
$firstDate = str_replace($str2strip, "", $firstFile);

$files = scandir($directory, SCANDIR_SORT_DESCENDING);
$lastFile = $files[0];

$lastDate = str_replace($str2strip, "", $lastFile);
?>

<!DOCTYPE html>
<html>
   <head>
    <meta charset=utf-8 />
    <script type="text/javascript" src="https://code.jquery.com/jquery-3.5.1.js" crossorigin="anonymous"></script>
    <script type="text/javascript" src="https://cdn.datatables.net/1.10.21/js/jquery.dataTables.min.js"></script>
    <link rel="stylesheet" type="text/css" href="https://cdn.datatables.net/1.10.21/css/jquery.dataTables.min.css"/>
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
      <button style="float:right;" onclick="getPastResults()">Go</button>
      <input style="float:right;" type="date" id="myDate" min="<?php echo $firstDate ?>" max="<?php echo $lastDate ?>" value="<?php echo $lastDate ?>"/>
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
    <script type="text/javascript" src="script.js" /></script>
  </body>
</html>
