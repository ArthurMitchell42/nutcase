
window.addEventListener('DOMContentLoaded', () => {
  Display_Size()
})

$(window).resize(function() {
  Display_Size();
});

var globalResizeTimer = null;

function Display_Size() {
  Debug = document.getElementById("ph_debug")

  if(globalResizeTimer != null) window.clearTimeout(globalResizeTimer);
  globalResizeTimer = window.setTimeout(function() {
    var Code = "N/A";
    if (document.documentElement.clientWidth >= 1400 ) { Code = "xxl" } else {
      if (document.documentElement.clientWidth >= 1200 ) { Code = "xl" } else {
        if (document.documentElement.clientWidth >= 992 ) { Code = "lg" } else {
        if (document.documentElement.clientWidth >= 768 ) { Code = "md" } else {
        if (document.documentElement.clientWidth >= 576 ) { Code = "sm" }
          }
        }
      }
    }
    Debug.innerHTML = document.documentElement.clientWidth + " " + document.documentElement.clientHeight + " " + Code;
  }, 200);
}
