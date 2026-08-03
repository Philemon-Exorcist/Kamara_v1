# this is for describing what each does and how to use them for the agent
# TODO (canvas bounds): fill this in with the real coordinate space your
# frontend whiteboard uses (e.g. "x: 0-1920, y: 0-1080" or whatever tldraw
# viewport your React app is rendering). Every description below assumes such
# a bound exists so the model doesn't place shapes/text off-screen — right
# now nothing in the tool schema tells it what the usable area actually is.

draw_tool_desc = """
Draws one geometric shape on the student's whiteboard. This is your ONLY way
to put a visual shape/figure/diagram element on the board — there is no
separate "diagram" tool. Complex figures (graphs, force diagrams, geometric
constructions) must be built by calling this tool multiple times, once per
shape, combined with write_board for labels.

SUPPORTED SHAPES (tldraw only — you may only use these exact strings):
rectangle, ellipse, triangle, diamond, pentagon, hexagon, octagon, star,
rhombus, rhombus-2, oval, trapezoid, cloud, heart, arrow-right, arrow-left,
arrow-up, arrow-down, x-box, check-box

If asked for or thinking of a shape not on this list, translate to the
closest supported one before calling the tool. Common translations:
  circle          -> ellipse
  square          -> rectangle (set width == height)
  box             -> rectangle
  rounded rectangle -> rectangle
  sphere          -> ellipse
  arrow           -> arrow-right / arrow-left / arrow-up / arrow-down
                     (pick the direction that matches what you're pointing at)
Never pass a shape name that isn't in the supported list — pick the nearest
match instead of inventing a new string.

PARAMETERS
  shape_id (string, required)
    A short unique identifier for THIS shape, e.g. "circle1", "fraction_bar3".
    Do NOT include a "shape:" prefix yourself — the backend adds that prefix
    automatically when it stores the shape. Sending your own "shape:" prefix
    will double it up and the reference will break for later delete/move/
    resize calls. Keep every ID unique within the session so you can safely
    move, resize, or delete this exact shape later without touching others.

  shape (string, required)
    One of the exact supported shape strings above.

  x (integer, required)
    Horizontal position of the shape's top-left corner, in board coordinates.
  y (integer, required)
    Vertical position of the shape's top-left corner, in board coordinates.
    [CANVAS BOUNDS: fill in the real usable range here.]

  width (integer)
  height (integer)
    Size of the shape's bounding box, in the same units as x/y. ALWAYS
    provide both — the underlying function has no default values for these
    and will error if they're missing, even though they aren't currently
    marked "required" in the tool schema. For a square, set width == height.
    For a straight horizontal line (e.g. the bar of a fraction), use a very
    thin rectangle: small height (a few units), width spanning what the line
    needs to cover.

USAGE NOTES
  - Building a stacked fraction, exponent, or any notation that isn't plain
    text is a composition of multiple draw_on_board / write_board calls, not
    a single call — there is no native "fraction" or "superscript" primitive.
    Example for the fraction 2/3:
      1. write_board: "2" centered above the intended bar position
      2. async_draw: a thin rectangle (the dividing line) directly beneath it
      3. write_board: "3" centered directly beneath that rectangle
    Position all three using consistent x-centering so they read as one
    vertically-stacked unit rather than three unrelated items.
  - Keep shapes inside the usable canvas area — going outside it means the
    student can't see what you drew.
  - Reuse shape_ids you created earlier ONLY when you intend to move/resize/
    delete that specific shape (via move_item, adjust_item_size, delete_item)
    — never reuse an ID to mean a different, unrelated shape.
"""

write_tool_desc = """
Writes text — letters, words, numbers, mathematical symbols — onto the
whiteboard at a specific position. This is your ONLY way to put text on the
board. There is no built-in support for rich formatting (no bold/italic
flags, no automatic fraction or superscript rendering, no font selection) —
formatting is achieved entirely through what text you send, what size you
send it at, and where you position it relative to other text/shapes you've
already placed.

PARAMETERS
  text_id (string, required)
    A short unique identifier for THIS piece of text, e.g. "topic_header",
    "step1_line", "frac_numerator_2". Do NOT include a "shape:" prefix
    yourself — the backend adds it automatically. Keep every ID unique so you
    can move, resize, or delete this specific text later without affecting
    other content on the board.

  text (string, required)
    The literal text to render. Keep this to a SHORT chunk — a term, a
    single step of a calculation, a short phrase — never a full paragraph or
    a full multi-step equation in one call. Send successive short chunks
    across multiple write_board calls, timed with your speech, so the board
    fills in gradually rather than appearing all at once.

  x (integer, required)
  y (integer, required)
    Position of the text's anchor point (top-left of the text block), in
    board coordinates. [CANVAS BOUNDS: fill in the real usable range here.]
    Use these to align related pieces of text precisely — e.g. to center a
    numerator over a denominator, give both write_board calls the same
    horizontal center, not just eyeballed-close x values.

  text_size (integer, required)
    Font size in board units. Use a clearly larger size for the lesson
    topic/header (Section 5 of the tutor prompt), a standard body size for
    normal explanation and equations, and a visibly smaller size for
    superscripts/subscripts (exponents, chemical-formula subscripts) —
    positioned slightly above (superscript) or below (subscript) and to the
    right of the base text's own x/y, not at the same size and baseline.

USAGE NOTES
  - There is no radical (√), Greek-letter, or other special-symbol guarantee
    beyond whatever characters the frontend's text renderer supports — if a
    needed symbol doesn't render correctly, prefer writing it out in words
    (e.g. "square root of x") rather than risk an unreadable glyph.
  - Fractions: render as text-over-line-over-text using three separate calls
    (see draw_tool_desc's usage notes) — never send a fraction as flat inline
    text like "2/3".
  - Never pack an entire sentence, full equation, or multi-line explanation
    into a single write_board call — this breaks the gradual, human pacing
    the tutor is supposed to have.
"""

move_item_desc = """
Moves an existing item — a shape (from async_draw) or a piece of text (from
write_board) — to a new position on the whiteboard. This does NOT change its
size or content, only its location.

PARAMETERS
  item_id (string, required)
    The exact ID you originally used when creating this item with async_draw
    (shape_id) or write_board (text_id) — no "shape:" prefix, just the same
    bare identifier you assigned at creation time.

  x (integer, required)
  y (integer, required)
    The new top-left position for the item, in the same board coordinate
    system used by draw_on_board/write_on_board.
    [CANVAS BOUNDS: fill in the real usable range here.]

USAGE NOTES
  - Use this to tidy up the board (Section 6 of the tutor prompt) — e.g.
    nudging a worked example over to make room for a new one, or realigning
    a numerator/denominator pair that ended up slightly off-center — rather
    than deleting and redrawing content that's already correct.
  - You must already know the item's ID; if you don't have it (e.g. content
    from much earlier in the session you didn't track), it's safer to leave
    it in place or clear and redraw than to guess an ID.
"""

delete_tool_desc = """
Deletes ONE specific existing item — a shape or a piece of text — from the
whiteboard, identified by its ID. Use this for surgical removal of a single
item; use clear_whiteboard instead when you mean to wipe the whole board.

PARAMETERS
  item_id (string, required)
    The exact ID you originally used when creating this item with async_draw
    (shape_id) or write_board (text_id) — no "shape:" prefix, just the bare
    identifier you assigned at creation time.

USAGE NOTES
  - Use this when correcting a single mistake (e.g. you wrote a wrong sign
    or number and want to remove just that piece before writing the fix),
    or when tidying a small amount of now-irrelevant content, without
    disturbing anything else on the board.
  - Do not use this repeatedly as a substitute for clear_whiteboard when you
    actually want to reset a large area — deleting many small items one at a
    time is slower and more error-prone than one clear_whiteboard call
    followed by redrawing what should remain (e.g. the topic/date header).
"""

clear_tool_desc = """
Removes EVERYTHING currently on the whiteboard — every shape and every piece
of text, with no way to select what stays. There are no parameters.

USAGE NOTES
  - This wipes the topic/date header too. If you clear the board mid-session
    for space (Section 6 of the tutor prompt), you are responsible for
    deciding whether the header needs to be rewritten afterward — per the
    tutor prompt's session-start rules, the header is normally only set once
    at the very start of a session and treated as reserved space, so avoid
    calling clear_whiteboard for routine space management if it would also
    take out that header; prefer delete_item on specific old content instead
    when the header should persist.
  - Use this at the very start of a new session to guarantee a blank board
    before writing the topic and date, and any other time you deliberately
    want a full reset (e.g. moving to an entirely new sub-topic where nothing
    from before is still relevant).
"""

adjust_item_size_desc = """
Resizes an existing item's bounding box — works on shapes (from async_draw)
and text (from write_board) alike. This does NOT move the item's anchor
position or change its content/text — only its width and height.

PARAMETERS
  item_id (string, required)
    The exact ID you originally used when creating this item with async_draw
    (shape_id) or write_board (text_id) — no "shape:" prefix, just the bare
    identifier you assigned at creation time.

  width (integer, required)
  height (integer, required)
    The new size for the item, in the same units used at creation.

USAGE NOTES
  - Use this when something came out too large/small relative to the rest of
    the board, or when a fraction's dividing line needs to span a wider or
    narrower width to match a numerator/denominator that changed.
  - For text specifically, changing width/height here is a bounding-box
    resize, not a font-size change — if you actually mean "make this text
    bigger/smaller," you most likely want to delete_item it and recreate it
    with write_board using a different text_size instead.
"""



draw_line_tool_desc = """
Draws a straight line on the whiteboard, either horizontal or vertical. This is a convenience tool for simple lines; for angled lines or more complex
line work, use async_draw with a thin rectangle or a triangle shape instead.

PARAMETERS
  line_id (string, required)
    A short unique identifier for THIS line, e.g. "axis_x", "divider1". Do NOT include a "shape:" prefix yourself — the backend adds that prefix automatically when it stores the line. Keep every ID unique within the session so you can safely move, resize, or delete this exact line later without touching others.

  x (integer, required)
  y (integer, required)
    Position of the line's anchor point (top-left of the line's bounding box), in board coordinates. [CANVAS BOUNDS: fill in the real usable range here.]
    """