## Summary of Improvements

- **Documentation**: Clarified how to run the application locally, execute the automated test suite, and deploy using either Docker or the existing GitHub Actions CI/CD workflow.
- **User Interface**: Refreshed the Wordle board layout with improved spacing, typography, and button styling for a more modern look while preserving existing game behaviour.

## How to Use the Updates

- **Run locally**: Follow the updated sections in `README.md` under **Installation & Setup** and **Running Locally** to create a virtual environment, install dependencies, and start the Flask app.
- **Run tests**: Use the commands in the **Running Tests** section of `README.md` (`pytest` for a quick run, or `pytest --cov=...` for a full coverage run).
- **Deploy**: Either build and run the Docker image manually or rely on the GitHub Actions workflow, which builds the image and calls `scripts/deploy.sh` on pushes to `main` (once the required secrets are configured).

## Notes

- All changes are backwards‑compatible with the existing API and backend logic.
- The UI changes are purely presentational and do not alter how guesses, games, or players are processed.


