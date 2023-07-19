let container = document.getElementById("container");

toggle = (ele) => {
  container.classList.toggle("sign-in");
  container.classList.toggle("sign-up");
  console.log('clicke')

};

setTimeout(() => {
  container.classList.add("sign-in");
}, 200);
