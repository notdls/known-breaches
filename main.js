function getDatasets(){
    var hr = new XMLHttpRequest();
    hr.open("GET", "datasets/combined.json", true)
    hr.setRequestHeader("Content-type", "application/json", true);
    hr.onreadystatechange = function() {
        if (hr.readyState == 4 && hr.status == 200) {
            var data = JSON.parse(hr.responseText);
            buildTable(data);
        }
    }
    hr.send(null);
}

function buildTable(data){
    var table_div = document.getElementById('breach_div');
    const nf = new Intl.NumberFormat();
    var new_table = '<table id="breach_table" class="table table-bordered table-hover table-striped"><thead><tr><th scope="col">Record Count</th><th scope="col">Name</th><th scope="col">Dump Date</th><th scope="col">Info</th><th scope="col">Source</th></tr></thead><tbody>';
    for (var x = 0; x < data.length; x++){
        if (data[x].info == undefined) {
            data[x].info = "N/A";
        }
        if (data[x].breach_date == undefined) {
            data[x].breach_date = "N/A";
        }
        new_table = new_table + "<tr><td>" + nf.format(data[x].record_count) + "</td><td>" + data[x].dump_name + "</td><td>" + data[x].breach_date +"</td><td>" + data[x].info +"</td><td>" + data[x].source +"</td></tr>";  
    };
    new_table = new_table + "</tbody></table>";
    table_div.innerHTML = new_table;
    $('#breach_table').DataTable();
}