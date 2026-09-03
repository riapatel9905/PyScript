const nameInput = document.getElementById("name");
const emailInput = document.getElementById("email");
const rating = document.getElementById("rating");
const ratingValue = document.getElementById("ratingValue");
const form = document.getElementById("feedbackForm");

rating.oninput = function () {
  ratingValue.innerText = rating.value;
};


nameInput.oninput = function () {
  nameInput.value = nameInput.value.replace(/[^A-Za-z]/g, "");
};

form.onsubmit = function (e) {
  e.preventDefault();

  if (!emailInput.value.includes("@")) {
    alert("Please enter a valid email");
    return;
  }

  alert("Thank you for your feedback!");
  form.reset();
  ratingValue.innerText = "3";
};
