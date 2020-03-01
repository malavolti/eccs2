/* Formatting function for row details - modify as you need */
function format ( d ) {
    // `d` is the original data object for the row
    return '<table cellpadding="5" cellspacing="0" border="0" style="padding-left:50px;">'+
        '<tr>'+
            '<td>IdP DisplayName:</td>'+
            '<td>'+d.displayName+'</td>'+
            '<td></td>'+
        '</tr>'+
        '<tr>'+
            '<td>Technical Contacts:</td>'+
            '<td>'+d.contacts.technical+'</td>'+
            '<td></td>'+
        '</tr>'+
        '<tr>'+
            '<td>SP1:</td>'+
            '<td>'+d.sp1.entityID+'</td>'+
            '<td>'+d.sp1.status+'</td>'+
        '</tr>'+
        '<tr>'+
            '<td>SP2:</td>'+
            '<td>'+d.sp2.entityID+'</td>'+
            '<td>'+d.sp2.status+'</td>'+
        '</tr>'+
    '</table>';
}
 
$(document).ready(function() {
    var table = $('#example').DataTable( {
        "ajax": { 
           "url": "data.json",
           "dataSrc": ""
        },
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
              "data": "contacts.technical",
              "defaultContent": ''
            },
            { 
              "data": "contacts.support",
              "defaultContent": ''
            },
            { "data": "date" },
            { "data": "status" }
        ],
        "rowCallback": function( row, data, index ) {
          if (data.status == "ERROR") {
            $('td', row).css('background-color', 'Red');
          }
          if (data.status == "DISABLE") {
            $('td', row).css('background-color', 'Grey');
          }
          if (data.status == "OK") {
            $('td', row).css('background-color', 'Green');
          }
        },
        "order": [[1, 'asc']]
    } );
     
    // Add event listener for opening and closing details
    $('#example tbody').on('click', 'td.details-control', function () {
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
} );
