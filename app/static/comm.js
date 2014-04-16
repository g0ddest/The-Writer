var formShown = false;
var commDiv = document.createElement("div");
commDiv.id = "commAddDiv";

function showForm(id)
	{
		var currentNode = document.getElementById(id);
		if (formShown == false)
		{
			var form="<table> \
				<tr><td>Just type in there:</td></tr> \
				<tr><td><textarea id='commtext' cols='60' rows='8'></textarea></td></tr> \
				<tr><td><button id='submit' onclick=\"commPost('" + id + "')\">Add comment</button></td></tr> \
				</table>";
			commDiv.innerHTML = form;
			if (id == 'commnew') {currentNode.parentNode.appendChild(commDiv);}
			else {currentNode.parentNode.parentNode.appendChild(commDiv);}
			showForm.preserve = currentNode.innerHTML
			currentNode.innerHTML = "Click again to hide that stuff";
			formShown = true;
		}
		else
		{
			if (id == 'commnew'){currentNode.parentNode.removeChild(commDiv);}
			else {currentNode.parentNode.parentNode.removeChild(commDiv);}
			currentNode.innerHTML = showForm.preserve;
			formShown = false;
		}
	};

function commPost(id)
	{
		var ansRef = "";
		if (id != 'commnew'){
			var num = id.split('_');
			id = 'idval_' + num[1];
			ansRef = document.getElementById(id).value;
			num = null;
		}
		else {ansRef = 'new';}
		var text = $('#commtext').val();
		if (text == "") 
		{
			alert('Зачем нам в базе пустые поля, вы не думали?'); 
		}
		else
		{
		$.post(
	            "",
	            { commtext: text, ansref: ansRef },
	            function() { window.location.reload()}
	    );
		}
	};
