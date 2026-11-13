const cards = [...document.querySelectorAll('.service-card')];
const filters = document.querySelector('#service-filters');
const status = document.querySelector('#service-status');
const buttons = [...filters.querySelectorAll('[data-filter]')];

function filterServices(selectedButton) {
  const selectedTopic = selectedButton.dataset.filter;

  for (const card of cards) {
    card.hidden = selectedTopic !== 'all' && card.dataset.topic !== selectedTopic;
  }

  for (const button of buttons) {
    button.setAttribute('aria-pressed', String(button === selectedButton));
  }

  const count = cards.filter((card) => !card.hidden).length;
  status.textContent = count === 1 ? '1 service shown.' : `${count} services shown.`;
}

for (const button of buttons) {
  button.addEventListener('click', () => filterServices(button));
}

filters.hidden = false;
status.hidden = false;
filterServices(buttons[0]);

const form = document.querySelector('#guide-form');
const topic = document.querySelector('#topic');
const result = document.querySelector('#guide-result');
const title = document.querySelector('#next-title');
const detail = document.querySelector('#next-detail');
const answer = document.querySelector('#next-answer');

form.hidden = false;

topic.addEventListener('change', () => {
  result.hidden = true;
});

form.addEventListener('submit', (event) => {
  event.preventDefault();

  const card = cards.find((item) => item.dataset.topic === topic.value);
  if (!card) return;

  title.textContent = card.querySelector('h3').textContent;
  detail.textContent = card.querySelector('h3 + p').textContent;

  const paragraphs = [...card.querySelectorAll('.service-answer p')];
  answer.replaceChildren(
    ...paragraphs.map((paragraph) => {
      const copy = document.createElement('p');
      copy.textContent = paragraph.textContent;
      return copy;
    })
  );

  result.hidden = false;
  title.focus();
});
