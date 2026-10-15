// Tiny self-check widgets. No network, no storage: nothing here is graded or saved.
//
// <div class="quiz" data-answer="b" data-why="Because...">
//   <p>Question</p>
//   <button data-choice="a">Option A</button> <button data-choice="b">Option B</button>
//   <div class="feedback" role="status"></div>
// </div>
document.querySelectorAll(".quiz").forEach((quiz) => {
  const feedback = quiz.querySelector(".feedback");
  quiz.querySelectorAll("button[data-choice]").forEach((button) => {
    button.addEventListener("click", () => {
      const right = button.dataset.choice === quiz.dataset.answer;
      feedback.className = "feedback " + (right ? "ok" : "no");
      feedback.textContent = (right ? "Yes. " : "Not quite. ") + (quiz.dataset.why || "");
    });
  });
});

// Relationship picker: answers the two questions from the tutorial.
const picker = document.getElementById("picker");
if (picker) {
  const aMany = picker.querySelector("#a-many");
  const bMany = picker.querySelector("#b-many");
  const out = picker.querySelector("output");
  const answers = {
    "no,no": "One-to-one. Each A has exactly one B and each B belongs to exactly one A. In Django: OneToOneField. Example: a user and their profile.",
    "yes,no": "One-to-many. Each B belongs to one A, and one A has many Bs. In Django: a ForeignKey on B pointing to A. Example: one author, many recipes.",
    "no,yes": "One-to-many the other way round. Each A belongs to one B, and one B has many As. In Django: a ForeignKey on A pointing to B.",
    "yes,yes": "Many-to-many. Many As relate to many Bs. In Django: ManyToManyField (or an explicit 'through' model when the link itself carries data, such as a quantity). Example: recipes and tags.",
  };
  const update = () => {
    out.textContent = answers[aMany.value + "," + bMany.value];
  };
  aMany.addEventListener("change", update);
  bMany.addEventListener("change", update);
  update();
}
