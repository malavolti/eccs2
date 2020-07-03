<!DOCTYPE html>
<html>
   <head>
 
      <script type="text/javascript" src="https://code.jquery.com/jquery-3.5.1.js"></script>
      <script type="text/javascript" src="https://cdn.datatables.net/1.10.21/js/jquery.dataTables.min.js"></script>
      <link rel="stylesheet" type="text/css" href="https://cdn.datatables.net/1.10.21/css/jquery.dataTables.min.css"/>

      <script type="text/javascript" src="script.js"></script>
      <link href="style.css" rel="stylesheet" type="text/css" />

    <meta charset=utf-8 />
    <title>eduGAIN Connectivity Check Service 2</title>
  </head>
  <body>
    <hr>
    <div id="status">
      <input type="checkbox" name="status" value="ERROR">ERROR</input>
      <input type="checkbox" name="status" value="OK">OK</input>
      <input type="checkbox" name="status" value="DISABLE">DISABLE</input>
      <button style="float:right;" onclick="getPastResults()">Go</button>
      <input style="float:right;" type="date" id="myDate" min="2020-07-03" max="<?php echo date("Y-m-d")?>" value="<?php echo date("Y-m-d")?>"/>
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
  </body>
</html>
