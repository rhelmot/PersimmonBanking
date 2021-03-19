const Keyboard = {
  elements: {
      main: null,
      keysContainer: null,
      keys:[]
  },

  eventHandlers: {
      oninput: null,
      onclose: null
  },

  properties: {
      value: "",
      capslock: false

  },

  init() {
    //   making the elements
    this.elements.main = document.createElement("div");
    this.elements.keysContainer = document.createElement("div");

    // setting elements up
      this.elements.main.classList.add("keyboard","keyboard--hidden");
      this.elements.keysContainer.classList.add("keyboard_keys");
      this.elements.keysContainer.appendChild(this._createKeys());

      this.elements.keys = this.elements.keysContainer.querySelectorAll(".keyboard_key");
    // Add to DOM
    this.elements.main.appendChild(this.elements.keysContainer);
    document.body.appendChild(this.elements.main);

    //auto use
    document.querySelectorAll(".use-otpkeyboard-input").forEach(element =>{
        element.addEventListener("focus", () =>{
            this.open(element.value, Currentvalue =>{
                element.value= Currentvalue;
            });
        });
    });
  },

  _createKeys(){
      const fragment = document.createDocumentFragment();
      const keyLayout =[
          "1", "2", "3",
          "4", "5", "6",
          "7", "8", "9",
          "done", "0", "backspace"
      ];

      //create icon HTML
      const createIconHTML = (icon_name) => {
            return `<i class="material-icons">${icon_name}</i>`;
        };

      keyLayout.forEach(key => {
          const keyElement = document.createElement("button");
          const insertLineBreak = ["3","6", "9"].indexOf(key)!== -1;

          //attributes
          keyElement.setAttribute("type","button");
          keyElement.classList.add("keyboard_key","keyboard_key--wide",);

          switch (key){
              case "backspace":
                  keyElement.innerHTML= createIconHTML("backspace");
                  keyElement.addEventListener("click", () =>{
                      this.properties.value = this.properties.value.substring(0,this.properties.value.length-1);
                      this._triggerEvent("oninput");
                  });
                  break;

              case "done":
                  keyElement.classList.add("keyboard_key-dark");
                  keyElement.innerHTML= createIconHTML("check_circle");

                  keyElement.addEventListener("click", () =>{
                      this.close()
                      this._triggerEvent("oninput");
                  });
                  break;

              default:
                  keyElement.textContent = key.toLowerCase();
                  keyElement.addEventListener("click", () =>{
                      this.properties.value += key.toLowerCase();
                      this._triggerEvent("oninput");
                  });
                  break;
          }

          fragment.appendChild(keyElement);

          if(insertLineBreak){
              fragment.appendChild(document.createElement("br"))
          }

      });

      return fragment;
  },


  _triggerEvent(handlerName){
      if (typeof this.eventHandlers[handlerName] == "function"){
          this.eventHandlers[handlerName](this.properties.value);
      }
  },


  open(initialValue, oninput,onclose){
      this.properties.value = initialValue || "";
      this.eventHandlers.oninput = oninput;
      this.eventHandlers.onclose = onclose;
      this.elements.main.classList.remove("keyboard--hidden");
  },

  close() {
      this.properties.value = "";
      this.eventHandlers.oninput = oninput;
      this.eventHandlers.onclose = onclose;
      this.elements.main.classList.add("keyboard--hidden");
  }
};

window.addEventListener("DOMContentLoaded",function(){
    Keyboard.init();
});
