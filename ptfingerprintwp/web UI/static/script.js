function disableButton() {
  var button = document.getElementById("scan-btn");
  var scanningMessage = document.getElementById("scanning-message");
  var domainInput = document.getElementById("website-input");
  var domainPlaceholder = document.getElementById("domain-placeholder");
  var scanContainer = document.getElementById("scan_container");
  var content = document.getElementById("container");
  var domain = domainInput.value;
  domainPlaceholder.textContent = domain;

  content.style.filter = "blur(9px)";
  button.style.display = "none";
  scanContainer.style.display = "none";
  button.innerHTML = "Enviando..."; // Opcionalmente, você pode alterar o texto do botão após a submissão.
  scanningMessage.style.display = "block";
}

function disableButtonScam() {
  var content = document.getElementById("container2");
  var button = document.getElementById("btn");
  var scanningMessage = document.getElementById("scanning-message2");
  var scanContainer = document.getElementById("container_hero");

  content.style.filter = "blur(9px)";
  button.style.display = "none";
  scanContainer.style.display = "none";
  scanningMessage.style.display = "block";
}


