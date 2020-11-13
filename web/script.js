// Needed to draw the ECCS2 DataTable
var table;
var url = "/eccs2/api/eccsresults?eccsdt=1";

// PHP Variables retrieved from eccs2.php
// idp (entityID of the IdP)
// date (date time of the check)
// reg_auth (the IdP RegistrationAuthority)
// status (the ECCS2 IdP Status)
if (date) {
   url = url.concat("&date=" + date);
}
if (reg_auth) {
   url = url.concat("&reg_auth=" + reg_auth);
}
if (idp) {
   url = url.concat("&idp=" + idp);
}
if (status) {
   url = url.concat("&status=" + status);
}


function getPastResults() {
   url = "/eccs2/api/eccsresults?eccsdt=1&date=" + document.getElementById("myDate").value;
   table.ajax.url( url ).load();
  
   var getUrl = window.location;
   var baseUrl = getUrl .protocol + "//" + getUrl.host + "/" + getUrl.pathname.split('/')[1];

   document.location.href = baseUrl;
}

// use URL constructor and return hostname
function getHostname(url) {
   if (url == ""){
      return null
   }
   const urlNew = new URL(url);
   if (urlNew.hostname){
      return urlNew.hostname;
   }
   else {
      return url.replace(/.+:/g, '');
   }
}

/* Formatting function for row details - modify as you need */
function format ( d ) {
    // `d` is the original data object for the row
    return '<table id="inner-table">'+
        '<tr>'+
            '<td class="strong">IdP DisplayName:</td>'+
            '<td>'+d.displayName+'</td>'+
        '</tr>'+
        '<tr>'+
            '<td class="strong">Technical Contacts:</td>'+
            '<td>'+d.contacts.technical+'</td>'+
        '</tr>'+
        '<tr>'+
            '<td class="strong">Support Contacts:</td>'+
            '<td>'+d.contacts.support+'</td>'+
            '<td class="strong">Check Time</td>'+
            '<td class="strong">Result Check</td>'+
            '<td class="strong">Status Code</td>'+
            '<td class="strong">Page Source</td>'+
            '<td class="strong">Retry Check</td>'+
        '</tr>'+
        '<tr>'+
            '<td class="strong">SP1:</td>'+
            '<td>https://'+getHostname(d.sp1.wayflessUrl)+'</td>'+
            '<td>'+d.sp1.checkTime+'</td>'+
            '<td>'+d.sp1.status+'</td>'+
            '<td>'+d.sp1.statusCode+'</td>'+
            '<td><a href="/eccs2html/'+d.date+'/'+getHostname(d.entityID)+'---'+getHostname(d.sp1.wayflessUrl)+'.html" target="_blank">Click to open</a></td>'+
            '<td><a href="'+d.sp1.wayflessUrl+'" target="_blank">Click to retry</a></td>'+
        '</tr>'+
        '<tr>'+
            '<td class="strong">SP2:</td>'+
            '<td>https://'+getHostname(d.sp2.wayflessUrl)+'</td>'+
            '<td>'+d.sp2.checkTime+'</td>'+
            '<td>'+d.sp2.status+'</td>'+
            '<td>'+d.sp2.statusCode+'</td>'+
            '<td><a href="/eccs2html/'+d.date+'/'+getHostname(d.entityID)+'---'+getHostname(d.sp2.wayflessUrl)+'.html" target="_blank">Click to open</a></td>'+
            '<td><a href="'+d.sp2.wayflessUrl+'" target="_blank">Click to retry</a></td>'+
        '</tr>'+
    '</table>';
}

$(document).ready(function() {
    // Setup - add a text input to each footer cell
    $('#eccstable thead tr').clone(true).appendTo( '#eccstable thead' );
    $('#eccstable thead tr:not(:eq(1)) th').each( function (i) {
        var title = $('#eccstable thead th').eq( $(this).index() ).text();
        if($(this).index() !=0 && $(this).index() !=5) $(this).html( '<input type="text" placeholder="Search '+title+'" style="text-align:center;width: 100%;" />' );
 
        $( 'input', this ).on( 'keyup change', function () {
            if ( table.column(i).search() !== this.value ) {
                table
                    .column(i)
                    .search( this.value )
                    .draw();
            }
        } );
    } );

    table = $('#eccstable').DataTable( {
        "responsive": "true",
        "ajax": { 
           "url": url,
           "dataSrc": ""
        },
        "lengthMenu": [[10, 30, 50, 100, -1], [10, 30, 50, 100, "All"]],
        "autoWidth": false,
        "dom": '<"top"lip>rt<"bottom"><"clear">',
        "columns": [
            {
              "className":      'details-control',
              "orderable":      false,
              "data":           null,
              "defaultContent": ''
            },
            { 
              "data": "displayName",
              "defaultContent": ''
            },
            { "data": "entityID" },
            { "data": "registrationAuthority" },
            { 
              "data": "date",
              "width": "180px",
              "className": "dt-body-center"
            },
            { 
              "data": "status",
              "className": "dt-body-center",
              "visible": false
            }
        ],
        "rowCallback": function( row, data, index ) {
          if (data.status == "ERROR") {
            //$('td', row).css('background-color', '#EA4335'); // NEW ECCS2
            $('td', row).css('background-color', '#EA3D3F'); // OLD ECCS
            //$('td', row).css('background-color', '#FF0000');
            //$('td', row).css('background-color', '#F22422');
          }
          if (data.status == "DISABLED") {
            $('td', row).css('background-color', '#FFFFFF');
          }
          if (data.status == "OK") {
            //$('td', row).css('background-color', '#34A853');
            //$('td', row).css('background-color', '#00CE00'); // NEW ECCS2
            $('td', row).css('background-color', '#72F81B'); // OLD ECCS
          }
        },
        "order": [[1, 'asc']]
    } );
     
    // Add event listener for opening and closing details
    $('#eccstable tbody').on('click', 'td.details-control', function () {
        var tr = $(this).closest('tr');
        var row = table.row( tr );
 
        if ( row.child.isShown() ) {
            // This row is already open - close it
            row.child.hide();
            tr.removeClass('shown');
        }
        else {
            // Open this row
            row.child( format(row.data()) ).show();
            tr.addClass('shown');
        }
    } );

    $('input:checkbox').on('change', function () {
       //build a regex filter string with an or(|) condition
       var sts = $('input:checkbox[name="status"]:checked').map(function() {
          return this.value;
       }).get().join('|');

       //filter in column 5, with an regex, no smart filtering, not case sensitive
       table.column(5).search(sts, true, false, false).draw(false);
    });

    // Handle click on "Expand All" button
    $('#btn-show-all-children').on('click', function(){
        // Enumerate all rows
        table.rows().every(function(){
            // If row has details collapsed
            if(!this.child.isShown()){
                // Open this row
                this.child(format(this.data())).show();
                $(this.node()).addClass('shown');
            }
        });
    });

    // Handle click on "Collapse All" button
    $('#btn-hide-all-children').on('click', function(){
        // Enumerate all rows
        table.rows().every(function(){
            // If row has details expanded
            if(this.child.isShown()){
                // Collapse row details
                this.child.hide();
                $(this.node()).removeClass('shown');
            }
        });
    });   

} );
