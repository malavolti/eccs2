// Global URL
//var url = "/eccs2/api/eccsresults?eccsdt=1";
var url = "/eccs2/api/eccsresults?eccsdt=1&date=" + document.getElementById("myDate").value;
var table;

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
            '<td>IdP DisplayName:</td>'+
            '<td>'+d.displayName+'</td>'+
        '</tr>'+
        '<tr>'+
            '<td>Technical Contacts:</td>'+
            '<td>'+d.contacts.technical+'</td>'+
        '</tr>'+
        '<tr>'+
            '<td>Support Contacts:</td>'+
            '<td>'+d.contacts.support+'</td>'+
            '<td>Check Time</td>'+
            '<td>Result Check</td>'+
            '<td>Status Code</td>'+
            '<td>Page Source</td>'+
            '<td>Retry Check</td>'+
        '</tr>'+
        '<tr>'+
            '<td>SP1:</td>'+
            '<td>https://'+getHostname(d.sp1.wayflessUrl)+'</td>'+
            '<td>'+d.sp1.checkTime+'</td>'+
            '<td>'+d.sp1.status+'</td>'+
            '<td>'+d.sp1.statusCode+'</td>'+
            '<td><a href="/eccs2html/'+d.date+'/'+getHostname(d.entityID)+'---'+getHostname(d.sp1.wayflessUrl)+'.html" target="_blank">Click to open</a></td>'+
            '<td><a href="'+d.sp1.wayflessUrl+'" target="_blank">Click to retry</a></td>'+
        '</tr>'+
        '<tr>'+
            '<td>SP2:</td>'+
            '<td>https://'+getHostname(d.sp2.wayflessUrl)+'</td>'+
            '<td>'+d.sp2.checkTime+'</td>'+
            '<td>'+d.sp2.status+'</td>'+
            '<td>'+d.sp2.statusCode+'</td>'+
            '<td><a href="/eccs2html/'+d.date+'/'+getHostname(d.entityID)+'---'+getHostname(d.sp2.wayflessUrl)+'.html" target="_blank">Click to open</a></td>'+
            '<td><a href="'+d.sp2.wayflessUrl+'" target="_blank">Click to retry</a></td>'+
        '</tr>'+
    '</table>';
}

function getPastResults() {
   url = "/eccs2/api/eccsresults?eccsdt=1&date=" + document.getElementById("myDate").value;
   table.ajax.url( url ).load();
}
 
$(document).ready(function() {
    table = $('#eccstable').DataTable( {
        "ajax": { 
           "url": url,
           "dataSrc": ""
        },
        "lengthMenu": [[10, 20, 30, 40, 50, 100, -1], [10, 20, 30, 40, 50, 100, "All"]],
        "autoWidth": false,
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
              "className": "dt-body-center"
            }
        ],
        "rowCallback": function( row, data, index ) {
          if (data.status == "ERROR") {
            $('td', row).css('background-color', '#EA4335');
          }
          if (data.status == "DISABLED") {
            $('td', row).css('background-color', '#FFFFFF');
          }
          if (data.status == "OK") {
            $('td', row).css('background-color', '#34A853');
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
