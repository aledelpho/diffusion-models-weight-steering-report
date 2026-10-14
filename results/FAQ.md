# FAQ: what I learned about diffusion transformers and their text encoders

*These are questions anyone who makes images with these models might ask, even if you never touch a weight. The
answers are what I found while editing one model, Krea-2, and they come with my doubts.*

Read them with the asterisks attached:

* **One model.** Everything here was measured on Krea-2. It may not hold for Flux, SD3, Qwen-Image or anything else.
* **Mostly one observer.** I labelled most of the pictures myself, and I knew the conditions. Where someone blind
  labelled them, I say so.
* **Small samples.** Most tests use a few characters at two to eight seeds.
* **Tips are not tests.** Each answer says what was tested and what is only my advice. Where I write "tip", I have
  not tested whether it helps.

The full evidence is in the [results](README.md) and in [the story](STORY.md).

---

## How these models work

### What is a diffusion transformer (DiT), and how is Krea-2 built?

Older models like SD 1.5 and SDXL draw with a **U-Net**. A U-Net is a network that shrinks the picture, works on it,
and grows it back. Text enters through cross-attention, a separate mechanism that lets the picture look up the
words.

A **diffusion transformer** works differently. It cuts the picture into patches and treats them like words: as
tokens. Then it passes them through a stack of identical **blocks**.

Krea-2 has **28 single-stream blocks**. "Single-stream" means the text tokens and the image tokens travel in the
same sequence and look at each other in the same attention.

Each block has two halves:

* **attention:** tokens exchange information;
* **MLP:** each token is transformed on its own.

When people say "edit block 23", they mean scaling the weights of one of these 28 blocks.
[More on the edit](20-method.md).

### What does the text encoder do, and why is it a whole language model now?

The image model never sees your words. A **text encoder** reads the prompt first and hands over a long list of
numbers, the **conditioning**. That list is everything the image model will ever know about what you wrote.

* **Older models:** CLIP, sometimes with T5.
* **Krea-2:** a full language model, Qwen3-VL-4B. It hands over 12 different readings of every word, taken at
  different depths of the language model.

A language model understands longer and more structured prompts. The cost is that it brings its own habits.
[Page 30](30-the-text-encoder.md) is about what happens when you edit it.

### Does it matter how I write my prompt?

**What I tested:** whether the way a prompt is written changes what an edit does. Reordered, as tags, with synonyms:
it changes the effect of a block edit about as much as changing the seed does. Changing the *subject* changes it a
lot. The pre-registered verdict was inconclusive ([page 24](24-wording.md)).

**What I saw but did not test:**

* With the same words, the order seems to move the pose and framing.
* Under strong text-encoder edits, the same prompt in different word orders can land in different genres.

**Tip:** if you compare two settings, keep the wording fixed. If you compare wordings, change only the wording.

### What does the model draw when I don't name a style?

**There is no single default.**

* My elf brawler, without its style words, came out **anime** every time: 9 of 9.
* Seven other characters, without "Western comics style", came back as **paintings or realistic renders**. Only
  one picture in 28 was anime.
* The empty prompt gave anime, realistic, anime, painting.

So each description carries its own fallback style ([page 30](30-the-text-encoder.md#every-character-has-its-own-fallback)).

**Tip:** if the style matters, name it. If you remove a style word, expect the character to pick its own style.

### Why do some words drag in things I never asked for?

Single words carry strong priors. Each phrase alone, at four seeds:

* **"female dwarf"** is a woman **with a beard**, 4 of 4;
* **"uniform"** is an **anime schoolgirl**, 4 of 4;
* **"realistic western comics style"** draws **cowboys**: "western" is read as the Wild West.

This is described, not tested ([page 30](30-the-text-encoder.md#what-each-phrase-draws-alone)).

**Tip:** if something unexpected keeps appearing, render the suspicious words on their own at a few seeds. It is
the cheapest test there is.

### Why does my character come out more generic, or lighter-skinned?

I saw this when I weakened the conditioning with edits to two layers of the text encoder. Before the style changed,
the character lost what made it specific:

* the half-orc's orc features;
* the non-binary elf's androgynous look;
* the dwarf's armour and braids.

When the skin changed, it went **lighter in 52 of 53 cases**. A second person, who knew nothing about the study,
saw the same: 14 of 14. Random pushes of the same size almost never changed the skin. This was pre-registered
([page 30](30-the-text-encoder.md#what-the-edit-costs-the-character)).

None of my prompts named a skin tone. So when the model has less to go on, it falls back to its default, and its
default is lighter skin. Audits of other text-to-image models report the same tendency.

**What this does not show:** what happens with ordinary prompts, LoRAs or other models.

**Tip, untested:** if a trait matters (skin tone, age, a non-human feature), write it explicitly, and check it at
several seeds.

### Why does the model ignore some details whatever I do?

Over eight seeds of the unedited model, some details were **never drawn**:

* my dwarf's scars;
* my half-orc's tusks, dirt smudges and snarl.

The elf had almost every trait at every seed; the smirk was missing once in eight
([page 30](30-the-text-encoder.md#what-the-edit-costs-the-character)).

**Tip:** before blaming your LoRA, sampler or edit for a missing detail, check whether the plain model draws it
at all. Use more than one seed.

---

## If you tune, edit or add things (LoRAs, presets, block weights)

### Do early, middle and late blocks do different things?

In Krea-2, yes, roughly:

* **The blocks near the output** behave like **surface controls**. The layout stays, while colour, grain and
  sharpness move. They are also the first to show artefacts when pushed.
* **The middle blocks** change **content**: viewpoint, identity, medium. They are the least predictable.

My map of the 28 blocks is by eye and still open, but one practical claim was tested blind on comics and cartoons:
editing blocks 1–19 changes the picture more than editing blocks 20–27, and damages its surface far less often
(**19% of pairs against 79%**) ([page 21](21-block-map.md), [page 29](29-inside-the-block.md)).

**Tip:** tools that weight a LoRA block by block (for example sd-webui-lora-block-weight) rely on the same idea.
My edit scales the base weights, not a LoRA, and only on Krea-2. Take this map as a place to start looking, not
a rule.

### Where does the noise come from when an edit or a LoRA is too strong?

Mostly from the **MLP half** of a block. Pushed at the same dose, the MLP was the noisier half in 13 of 19 cells. The
attention added noise only at the very end of the stack. This was labelled blind, but without a rule fixed in
advance, so it is still open ([page 29](29-inside-the-block.md)).

The text encoder behaves differently. Doubling one of its layers changes the **genre and the character** of the
picture, and costs less surface quality than an image-model preset ([page 30](30-the-text-encoder.md)).

### Is there a simple way to change saturation?

In Krea-2, **block 23** works like a saturation knob:

* Slightly above 1, it lowers saturation; slightly below, it raises it. The response is monotonic and roughly
  proportional to the dose.
* At the same colour gain, it disturbs the picture less than adding "colorful, vivid" to the prompt. The words also
  redraw things: they turned a cartoon elf blonde and added a lemon to a still life.

It is not cleaner than a saturation slider applied afterwards: it regenerates the picture
([page 22](22-saturation-knob.md)).

**Tip:** words in the prompt change more than the thing they name. If you only want colour, change only colour.

### Will an edit, or a LoRA, do the same thing to every character?

It depends where the edit acts.

* **In the image model**, a preset I wrote by eye on four portraits changed three characters it had never seen in
  the same direction. A blind observer picked it as the closer match to my description **56 of 56 times**. The
  faces still moved more than a change of seed would move them ([page 28](28-portrait-preset.md)).
* **In the text encoder**, a single edit moved different characters in different directions. Only 4 of 20 edits
  were coherent ([page 30](30-the-text-encoder.md)).

### How strong is "strong"?

My edits scale weights by 1 + d. Scaling all three matrices of an MLP by 2 can multiply that layer's output by up to
about **8** (this is an estimate).

Along a dose ladder, the style of a portrait **did not change below about d = 0.70**, and no picture fell apart even
at full dose. What went first was the **character** ([page 30](30-the-text-encoder.md#a-dose-ladder)).

**Tip:** "nothing changed" at low strength does not mean nothing is happening. Check the details you care about,
not only the overall look.

### Can I trust image-quality metrics (CLIP-IQA, BRISQUE, LPIPS, DINOv2)?

For some things.

* **They agreed with my eye on colour and on surface damage.**
* **They missed what mattered most:** the change of *content* made by the middle blocks. I predicted DINOv2 would
  see it, and it did not ([page 25](25-standard-metrics.md)).
* **A statistic of line work I relied on early could not rank edits by damage at all** ([page 26](26-what-did-not-work.md)).

**Tip:** a metric that does not move is not proof that nothing changed. Look at the pictures.

### What is the cheapest honest way to test a LoRA, a preset or a setting?

What I learned, often the hard way:

1. **Same seed, same everything else.** Render the baseline and the variant from one pipeline.
   * In ComfyUI a re-render can be identical pixel for pixel. If it is not, something else is changing.
2. **Decide what counts as success before you look.** Write it down, with a number if you can.
   * Several of my early "findings" did not survive this ([what did not work](26-what-did-not-work.md)).
3. **Look side by side.** In my experience, comparing pictures next to each other was far more consistent than
   judging one picture at a time.
4. **Ask someone who does not know which is which.**
   * Give them the description of the look you want, and the pair, in random order.
   * You can try it on my preset: [the blind test](https://aledelpho.github.io/krea2-weight-knobs-results/try-the-test.html).
5. **Use more than one seed and more than one subject.** An effect on one picture is an anecdote.
6. **Compare with a fair control.**
   * For example, a random change of the same size.
   * Some of my edits were special; some were no better than noise.

### Does this apply to my model?

I do not know. Everything here is Krea-2 with one tuner. The method travels; the specific blocks and layers
probably do not. If you try it on another model, I would like to hear what you find.
