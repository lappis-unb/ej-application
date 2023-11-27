const manageNextCommentTransition = () => {
  $(".voting-card__comment")[0].style.opacity = "0";
  $(".voting-card__comment")[0].classList.remove("voting-card__comment--show");
  setTimeout(() => {
    $(".voting-card__comment")[0].classList.add("voting-card__comment--show");
  }, 500);
  $("form")[0].addEventListener("htmx:afterRequest", () => {
    manageNextCommentTransition();
  });
};

const addsNextCommentTransitionEvent = () => {
  $("form")[0].addEventListener("htmx:afterRequest", () => {
    manageNextCommentTransition();
  });
};

window["addsNextCommentTransitionEvent"] = addsNextCommentTransitionEvent;
