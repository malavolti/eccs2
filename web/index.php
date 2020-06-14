<!DOCTYPE html>
<html>
   <head>
 
      <script type="text/javascript" src="https://code.jquery.com/jquery-3.4.1.js"></script>
      <script type="text/javascript" src="https://cdn.datatables.net/1.10.20/js/jquery.dataTables.min.js"></script>
      <link rel="stylesheet" type="text/css" href="https://cdn.datatables.net/1.10.20/css/jquery.dataTables.min.css"/>

      <script type="text/javascript" src="script.js"></script>
      <link href="style.css" rel="stylesheet" type="text/css" />

    <meta charset=utf-8 />
    <title>eduGAIN Connectivity Check Service 2</title>
  </head>
  <body>
    <hr>
    <div id="status">
      <input type="checkbox" name="status" value="ERROR">ERROR
      <input type="checkbox" name="status" value="OK">OK
      <input type="checkbox" name="status" value="DISABLE">DISABLE
    </div>
    <hr>
    <div class="container">
      <table id="eccstable" class="display" style="width:100%">
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
