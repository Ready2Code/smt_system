var dict = {};


$(function() {
	registerWords();

	if(null == localStorage.getItem("lang")) {
		 localStorage.lang = "en"
  }

  setLanguage(localStorage.lang);

	$("#enBtn").bind("click", function() {
		setLanguage("en");
	});

	$("#zhBtn").bind("click", function() {
		setLanguage("zh");
	});

	$("#applyBtn").bind("click", function() {
		alert(__tr("a translation test!"));
	});

});


function setLanguage(lang) {

	localStorage.lang=lang;
	translate();
}

function translate() {
	loadDict();
	$("[lang]").each(function() {
		switch (this.tagName.toLowerCase()) {
			case "input":
				$(this).val( __tr($(this).attr("lang")) );
				break;
			default:
				$(this).text( __tr($(this).attr("lang")) );
		}
	});
}

function __tr(src) {
	return (dict[src] || src);
}

function loadDict() {
	var lang = (localStorage.lang || "en");
	if(lang == "en") {
		dict = dict_en;
	}else if(lang == "zh") {
		dict = dict_zh;
	}

}

function registerWords() {
	$("[lang]").each(function() {
		switch (this.tagName.toLowerCase()) {
			case "input":
				$(this).attr("lang", $(this).val());
				break;
			default:
				$(this).attr("lang", $(this).text());
		}
	});
}

