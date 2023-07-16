document.addEventListener("DOMContentLoaded", function() {
    function autocomplete(inp, arr) {

      let currentFocus;



      inp.addEventListener("input", function(e) {
          let a, b, i, val = this.value;

          closeAllLists();
          if (!val) { return false;}
          currentFocus = -1;

          a = document.createElement("DIV");
          a.setAttribute("id", this.id + "autocomplete-list");
          a.setAttribute("class", "autocomplete-items");

          this.parentNode.appendChild(a);

          for (i = 0; i < arr.length; i++) {

            if (arr[i].substr(0, val.length).toUpperCase() == val.toUpperCase()) {

              b = document.createElement("DIV");

              b.innerHTML = "<strong>" + arr[i].substr(0, val.length) + "</strong>";
              b.innerHTML += arr[i].substr(val.length);

              b.innerHTML += "<input type='hidden' value='" + arr[i] + "'>";

                  b.addEventListener("click", function(e) {

                  inp.value = this.getElementsByTagName("input")[0].value;

                  closeAllLists();
              });
              a.appendChild(b);
            }
          }
      });
      /*execute a function presses a key on the keyboard:*/
      inp.addEventListener("keydown", function(e) {
          let x = document.getElementById(this.id + "autocomplete-list");
          if (x) x = x.getElementsByTagName("div");
          if (e.keyCode == 40) {

            currentFocus++;

            addActive(x);
          } else if (e.keyCode == 38) { //up

            currentFocus--;

            addActive(x);
          } else if (e.keyCode == 13) {

            e.preventDefault();
            if (currentFocus > -1) {

              if (x) x[currentFocus].click();
            }
          }
      });
      function addActive(x) {

        if (!x) return false;

        removeActive(x);
        if (currentFocus >= x.length) currentFocus = 0;
        if (currentFocus < 0) currentFocus = (x.length - 1);
        /*add class "autocomplete-active":*/
        x[currentFocus].classList.add("autocomplete-active");
      }
      function removeActive(x) {

        for (let i = 0; i < x.length; i++) {
          x[i].classList.remove("autocomplete-active");
        }
      }
      function closeAllLists(elmnt) {

        let x = document.getElementsByClassName("autocomplete-items");
        for (let i = 0; i < x.length; i++) {
          if (elmnt != x[i] && elmnt != inp) {
          x[i].parentNode.removeChild(x[i]);
        }
      }
    }

    document.addEventListener("click", function (e) {
        closeAllLists(e.target);
    });
    }

    let countries = ["United States", "UK", "Financials", "Industrials", "Tech", "Staples", "Real Estate", "Utilities",
                     "Health Care", "Consumer Discretionary", "Oil Services", "Mainland China", "Austria", "Belgium",
                     "Marine Shipping", "Chile", "Denmark", "Communications", "Metals", "Materials", "China", "Poland",
                     "ETF", "Australia", "Germany", "Japan", "Singapore", "Brazil", "Wind Power", "Crypto", "Finland",
                     "France", "Gold Miners", "Greece", "Indonesia", "Ireland", "Isreal", "Small Caps", "Transports",
                     "Airlines", "Saudi Arabia", "Lithium", "Malaysia", "Mexico", "Mid Caps", "Netherlands", "Portugal",
                     "Qatar", "Minerals", "Small Cap Growth", "High Dividend", "Semiconductors", "Silver Miners",
                     "South Africa", "South Korea", "Sweeden", "Solar", "Tawian", "Thailand", "Micro Chips", "Turkey", "UAE",
                     "Uranium", "Value", "Water", "Bitcoin Miners", "Lumber"
                    ]


    autocomplete(document.getElementById("myInput"), countries);




// const button = document.getElementById('myButton');
//
// button.addEventListener('click', function() {
//   button.classList.toggle('active');
// });



const observer = new IntersectionObserver((entries) => {

    entries.forEach((entry) => {

        if (entry.isIntersecting){
            entry.target.classList.add('show');
        }
        else{
            entry.target.classList.remove('show');
        }


    });
});

const hiddenElements = document.querySelectorAll('.hidden');
hiddenElements.forEach((el => observer.observe(el)));

});















