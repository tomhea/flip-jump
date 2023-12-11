# Introduction
First off, thank you for considering contributing to FlipJump. It's people like you that make the esoteric language community such a great, active and evolving community.

Following these guidelines helps to communicate that you respect the time of the developers managing and developing this open source project. In return, they should reciprocate that respect in addressing your issue, assessing changes, and helping you finalize your pull requests.

FlipJump is an open source project, and we love to receive contributions from our community — you!   
There are many ways to contribute, from writing tutorials or blog posts, writing new fj-programs, improving the documentation, submitting bug reports and feature requests or writing code which can be incorporated into the FlipJump source / standard-library itself.

Also, please take 2 minutes to show this project to the people you know that would **see the magic in this language.**

Please, don't use the issue tracker for support-questions. Instead, use the [Questions thread](https://github.com/tomhea/flip-jump/discussions/176), or the [Discussions](https://github.com/tomhea/flip-jump/discussions) in general. 

## Responsibilities
 * Ensure cross-platform compatibility for every change that's accepted. Windows & Ubuntu & Macos.
 * Ensure that code that goes into core passes the [ci-tests](tests/README.md#the-ci).
 * Create issues (+Discussions) for any major changes and enhancements that you wish to make. Discuss things transparently and get community feedback.
 * Don't change the stl-api, only offer new options. feel free to discuss it first.
 * Keep each PR as small as possible, preferably one new change/feature per PR.
 * Be welcoming to newcomers and encourage diverse new contributors from all backgrounds. See the [Python Community Code of Conduct](https://www.python.org/psf/codeofconduct/).

## Your First Contribution
Unsure where to begin contributing to FlipJump? You can start by creating and running your own FlipJump programs, on your own repos, and spread the rumor :)  
Also, please take a look at the [Contribution thread](https://github.com/tomhea/flip-jump/discussions/148).

Working on your first Pull Request? You can learn how from this free series, [How to Contribute to an Open Source Project on GitHub](https://app.egghead.io/playlists/how-to-contribute-to-an-open-source-project-on-github).

At this point, you're ready to make your changes! Feel free to ask for help; everyone is a beginner at first 😸

If a maintainer asks you to "rebase" your PR, they're saying that a lot of code has changed, and that you need to update your branch, so it's easier to merge.

# Getting started
1. Create your own fork of the code
2. Do the changes in your fork (keep them minimal).
3. If you like the change and think the project could use it:
    * Be sure you have followed the [code style](CONTRIBUTING.md#clean-code) for the project.
    * be sure your project passes the [ci-tests](tests/README.md#the-ci).
    * Send a pull request.

If you have **small or "obvious" fixes**, include SMALLFIX in the PR/issue name.
such fixes can be:
* Spelling / grammar fixes
* Typo correction, white space and formatting changes
* Comment clean up
* Functions/Classes rearrangements in the same file
It should still pass the [ci-tests](tests/README.md#the-ci).

# How to report a bug
When filing an issue, make sure to answer these five questions:

 1. What version of FlipJump are you using (if no version, make sure you fetched the last changes, and specify the branch name)?
 2. What operating system are you using?
 3. What did you do?
 4. What did you expect to see?
 5. What did you see instead?
General questions should go to the [Questions thread](https://github.com/tomhea/flip-jump/discussions/176), or the [Discussions](https://github.com/tomhea/flip-jump/discussions) in general. 

# How to suggest a feature or enhancement
The FlipJump philosophy is to be the simplest language of all, that can do any modern computation.

FlipJump should be below the OS, as it's a cpu-architecture after all.

The FlipJump stl should be minimalistic, efficient in both space and time, and offer macros similar to x86 ops.

The generic stl macro should look like `macro_name n dst src` for an n-bit/hex variable, with dst being the destination-variable, and src being the source-variable. (e.g. `hex.add n, dst, src`). 

If you find yourself wishing for a feature that doesn't exist, you are probably not alone. Some features that FlipJump has today have been added because our users saw the need. Open an issue on our issues list on GitHub which describes the feature you would like to see, why you need it, and how it should work.

## Code review process
After feedback has been given to the Pull Request, we expect responses within two weeks. After two weeks we may close the pull request if it isn't showing any activity.

# Community
You can chat with the core team and the community on [GitHub Discussions](https://github.com/tomhea/flip-jump/discussions).

# Clean Code
Get familiar with [Clean Code](https://gist.github.com/wojteklu/73c6914cc446146b8b533c0988cf8d29) (mainly the functions/names sections).

In short:
- use **clear names** (full words, **descriptive**, not-too-long), for variables, functions/macros (verb-name), and classes (nouns).
- **functions should do exactly one thing**. no side effects. They should be **very short** (and call other descriptive functions). IT IS POSSIBLE for a function to be 4-5 lines (and we should aim to that). 

Keep in mind that the developers of this community invested much of their time in making this project as clean, simple, and documented as they can. 

If you find a piece of code that isn't compliant with this standard, it probably has an open issue and is known, and if not, please open a new issue.  

Follow this rule but don't try to be perfect, and use the [80/20](https://en.wikipedia.org/wiki/Pareto_principle) principle. Yet, make an effort to make the code as simple, as much as you'd expect from others in this project's community.

