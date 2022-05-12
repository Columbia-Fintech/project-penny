

$(document).ready(function(){
    //when the page loads, display all the names
    $('#keyCSV').CSVToTable('key_values.csv')
    $('#lineCSV').CSVToTable('line_items.csv')
})