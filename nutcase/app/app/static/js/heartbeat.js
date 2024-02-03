var heartbeat_state = 0

function heartBeat(cmd) {
  icon = document.getElementById('heartbeat');
  // console.log("heartbeat_state: " + heartbeat_state)
  switch(cmd) {
    case "beat":
      heartbeat_state = 4
      icon.classList.remove("text-danger")
      icon.classList.add("text-success")
      break;
    case "error":
      heartbeat_state = -1
      icon.classList.remove("text-success")
      icon.classList.add("text-danger")
      break;
    default:
      if (heartbeat_state == 0) {
        break;
      }
      if (heartbeat_state == -2) {
        heartbeat_state = -1;
      } else {
        heartbeat_state -= 1;
      }
  } 

  icon.className = "";
  icon.classList.add("bi")
  icon.classList.add("fs-3")

  switch(heartbeat_state) {
    case 4:
      icon.classList.add("text-success")
      icon.classList.add("bi-heart-pulse-fill")
      break;
    case 3:
      icon.classList.add("text-success")
      icon.classList.add("bi-heart-pulse-fill")
      break;
    case 2:
      icon.classList.add("text-success")
      icon.classList.add("bi-heart-fill")
      break;
    case 1:
      icon.classList.add("text-success")
      icon.classList.add("bi-heart-fill")
      icon.classList.add("opacity-75")
      break;
    case 0:
      icon.classList.add("text-success")
      icon.classList.add("bi-heart-fill")
      icon.classList.add("opacity-50")
      break;
    case -1:
      icon.classList.add("text-danger")
      icon.classList.add("bi-heartbreak-fill")
      break;
    case -2:
      icon.classList.add("text-danger")
      icon.classList.add("bi-heart-fill")
      break;
    default:
      break
  } 
}

setInterval('heartBeat()', 1000 * 1); // Units: ms
// setInterval('heartBeat("error")', 1000 * 64); // Units: ms