const manageNextCommentTransition = () => {
  calculateCommentHeight();
  const commentElement = $(".voting-card__comment")[0];
  if(commentElement){
    commentElement.style.opacity = "0";
    commentElement.classList.remove("voting-card__comment--show");
    setTimeout(() => {
      commentElement.classList.add("voting-card__comment--show");
    }, 500);
    $("form")[0].addEventListener("htmx:afterRequest", () => {
      manageNextCommentTransition();
    });
  }
};

const calculateCommentHeight = () => {
  let commentHtmlElement = $(".voting-card__comment")[0];
  if (!commentHtmlElement) {
    commentHtmlElement = $(".voting-card__message")[0];
  }
  let clientHeight = commentHtmlElement.clientHeight;
  let fixedCommentHeight = clientHeight + 16;
  if (fixedCommentHeight < 150) {
    fixedCommentHeight = 150;
  }
  commentHtmlElement.style.height = `${fixedCommentHeight}px`;
};

window["addsNextCommentTransitionEvent"] = manageNextCommentTransition;
