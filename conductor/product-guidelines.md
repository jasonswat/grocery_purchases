# Product Guidelines: Grocery Purchase History Scraper

## Brand Identity: The Toolbox Approach
The project is a functional, no-nonsense utility designed for efficiency and reliability. It should feel like a reliable tool in a developer's or home manager's toolkit—powerful, precise, and focused on the task at hand.

## Communication Style: Professional & Technical
- **CLI Output:** Focus on clarity and technical accuracy. Provide meaningful status updates without unnecessary fluff.
- **Error Messages:** Be specific and technical. If a scraper fails due to a DOM change or a timeout, provide the technical context necessary to diagnose the issue.
- **Logs:** Maintain detailed logs for debugging purposes, following standard logging levels (DEBUG, INFO, WARNING, ERROR).

## UX Principle: Transparency
- **Actionable Status:** Always make it obvious what the tool is doing (e.g., "Navigating to Login Page", "Parsing Receipt #123").
- **Clear Progress:** Provide progress indicators for long-running scraping tasks.
- **Explicit Failures:** If a bot detection mechanism is triggered, clearly state this so the user understands why the process stopped.

## Design Principles
- **Modularity:** Each grocer should have its own self-contained scraper module, following a consistent interface.
- **Data Integrity:** Prioritize accurate data extraction over speed. If a value is ambiguous, it is better to flag it or skip it than to record incorrect data.
- **Resilience:** Design for intermittent network failures and website changes. Use robust selectors and retry logic where appropriate.
