function magic_error(form, message) {
    let elem = form.querySelector(".magic-error");
    elem.innerText = message;
	elem.style.display = "";
}

let magic_waiting = false;

function magic_submit(form) {
	if (magic_waiting) {
		return;
	}

	let success = null;
	let api = null;
	let toPost = {};
	for (let i = 0; i < form.elements.length; i++) {
		let elem = form.elements[i];
		if (elem.name === "_api") {
			api = elem.value;
		} else if (elem.name === "_success") {
			success = elem.value;
		} else if (elem.tagName !== "BUTTON") {
			toPost[elem.name] = elem.value;
		}
	}
	if (success === null || api === null) {
		magic_error(form, "This form is malformed!");
	}

	magic_waiting = true;
	let xhr = new XMLHttpRequest();
	xhr.responseType = "json";
	xhr.open("POST", api, true);
	xhr.onload = function () {
		if (xhr.readyState === 4) {
			magic_waiting = false;
			if (xhr.status === 200) {
				if ("error" in xhr.response) {
					magic_error(form, xhr.response.error);
				} else {
					location.href = success;
				}
			} else {
				magic_error(form, xhr.statusText);
			}
		}
	};
	xhr.onerror = function () {
		magic_waiting = false;
		magic_error(form, xhr.statusText);
	};
	xhr.send(JSON.stringify(toPost));
}

window.onload = function () {
	document.querySelectorAll(".magic-submit").forEach((elem) => {
		let form = elem;
		while (form.tagName !== "FORM") {
			form = form.parentElement;
		}
		elem.onclick = () => { magic_submit(form); }
	});
};
