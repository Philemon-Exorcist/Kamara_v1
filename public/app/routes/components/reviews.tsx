import reviewImage from "../../assets/hero2.jpg";

const reviewCards = [
  {
    quote:
      "The lessons feel clear, practical, and easy to follow. Kamara AI helped me study with more confidence.",
    name: "Lilian Patrick",
    rating: "4.9/5",
    initials: "LP",
  },
  {
    quote:
      "Perfect pacing, helpful guidance, and excellent course quality. Highly recommended.",
    name: "Osvaldo Winters",
    rating: "4.9/5",
    initials: "OW",
  },
  {
    quote:
      "This platform helped me redefine my study routine. Every collection feels fresh and modern.",
    name: "Brady Hinton",
    rating: "4.9/5",
    initials: "BH",
  },
];

const clientAvatars = ["AM", "JL", "RK"];

export function ReviewsSection() {
  return (
    <section className="reviews-section" aria-labelledby="reviews-heading">
      <div className="reviews-shell">
        <div className="reviews-intro reveal reveal-left">
          <h2 id="reviews-heading">What Our Happy Clients Say</h2>
          <p>
            Hear genuine feedback from our clients who trust us for quality,
            reliability, and great learning results.
          </p>

          <div className="reviews-avatar-row" aria-label="More than eighteen positive reviews">
            {clientAvatars.map((avatar) => (
              <span key={avatar}>{avatar}</span>
            ))}
            <strong>18+</strong>
          </div>
        </div>

        <div className="reviews-grid" aria-label="Client reviews">
          {reviewCards.slice(0, 2).map((review, index) => (
            <article className={`review-card reveal delay-${index + 1}`} key={review.name}>
              <span className="review-mark" aria-hidden="true">
                “
              </span>
              <p>{review.quote}</p>
              <footer>
                <span className="review-avatar">{review.initials}</span>
                <div>
                  <strong>{review.name}</strong>
                  <small>
                    <span aria-hidden="true">★</span> {review.rating}
                  </small>
                </div>
              </footer>
            </article>
          ))}

          <article className="review-card review-card-lower reveal delay-3">
            <span className="review-mark" aria-hidden="true">
              “
            </span>
            <p>{reviewCards[2].quote}</p>
            <footer>
              <span className="review-avatar">{reviewCards[2].initials}</span>
              <div>
                <strong>{reviewCards[2].name}</strong>
                <small>
                  <span aria-hidden="true">★</span> {reviewCards[2].rating}
                </small>
              </div>
            </footer>
          </article>

          <div className="review-photo reveal delay-4">
            <img src={reviewImage} alt="Smiling learner outdoors" />
          </div>
        </div>

        <div className="reviews-controls" aria-label="Review navigation">
          <button type="button" aria-label="Previous review">
            ←
          </button>
          <button type="button" aria-label="Next review">
            →
          </button>
        </div>
      </div>
    </section>
  );
}
