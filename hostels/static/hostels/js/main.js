const btn = document.getElementById("pageredirect")
function noRefresh() {
      window.location.href = "hostel/list/";
      document.AddEventListener("click")
    }


// Example starter JavaScript for disabling form submissions if there are invalid fields
(() => {
  'use strict'

  // Fetch all the forms we want to apply custom Bootstrap validation styles to
  const forms = document.querySelectorAll('.needs-validation')

  // Loop over them and prevent submission
  Array.from(forms).forEach(form => {
    form.addEventListener('submit', event => {
      if (!form.checkValidity()) {
        event.preventDefault()
        event.stopPropagation()
      }

      form.classList.add('was-validated')
    }, false)
  })
})()


//print a user booking
function printBooking(){
  const printContent = document.getElementById("print-content");
  const winPrint = window.open('', '', 'left=0, top=0, width=800, height=900, toolbar=0, scrollbars=0, status=0');
  winPrint.write(printContent.innerHTML);
  winPrint.close();
  winPrint.focus();
  winPrint.print();
  //winPrint.close();
}