<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>Test</title>
<script src="http://ajax.googleapis.com/ajax/libs/jquery/2.1.0/jquery.min.js"></script>

</head>
<body>

<script>
$(document).ready(function () { 
  $(document.body).append('hello here is some citation <br />');
  
  get_citations = function(id) {
    $.getJSON("http://nupubs.cogs.indiana.edu/collection/citations/" + id, function(data) {
      alert("gotta dem citations blong colection");
      var items = [];
      $.each(data, function (i, item) {
        items.push("<li id='" + item.citation_id + "'>" + item.title + "</li>");
      });
      $("#citations").empty()
      $("#citations").append("Citations: <br /> <ul>" + items.join("") + "</ul>");
    });
  };
  $(document.body).append("<div id='menu'></div>");
  $(document.body).append("<div id='citations'>Citations <br /></div>");

  $.getJSON("http://nupubs.cogs.indiana.edu/collection/owner/pjcraig", function(data) {
    alert("success");
    var items = [];
    $.each(data, function (i, item) {
      items.push("<option value='" + item.collection_id + "'>" + item.collection_name + "</option>" );
    });
    console.log(data);
    console.log(items);
    $("#menu").append("<select id='collections' onchange=\" if(this.selectedIndex) get_citations(this.value);\">" + items.join("") + "</select>");
  });
    
  
});
</script>
</body>
</html>
