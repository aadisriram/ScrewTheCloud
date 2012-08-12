function return_parity_table(objects,len)
{
    var table = document.createElement('TABLE');
    table.style.border = "thick solid #000000";    
    table.rules = "all"
    for (i in objects)
    {
	var row = table.insertRow(-1);
	var cell = row.insertCell(0);
	var row1 = 2*i;
	var row2 = 2*i+1;
	if (row2 == len)
	    row2 = 0;
	cell.innerHTML = '<p> Chunk \t#'+row1+'<br/> <br/> Chunk \t#'+row2+'</p>';
	//cell.innerHTML = '<div style="height:120px;width:200px;border:0 #ccc;font:16px/26px Georgia, Garamond, Serif;overflow:auto;">'+ 2*i + '<br/>' + (2*i+1)+'</div>';

	cell = row.insertCell(1);
	var str;
	if (objects[i].id == "im")
	    str = "Redundant backup stored on Imgur";
	else if (objects[i].id == "pb")
	    str = "Redundancy backup stored on Pastebin";
	else
	    str = "Redundancy backup stored on PloughTheCloud";	
	
	cell.innerHTML = str+'<a href='+objects[i].url+'>\t Click to view</a>';
    }
    return table
}
