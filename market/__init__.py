class OUTREACH:
    STATUS_CHOICES = [
        ('planned', 'Planned'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed')
        ]
    PROPERTY_TYPES = [
        ("MF", "Multifamily"),
        ("RT", "Retail"),
        ("HC", "Healthcare"),
        ("IN", "Industrial"),
        ("WH", "Warehouse"),
        ("MH", "Mobile Home Park"),
        ("OF", "Office"),
        ("MU", "Mixed Use"),
        ("LO", "Lodging"),
        ("HO", "Hospitality"),
        ("ST", "Student Housing"),
        ("SS", "Self-Storage"),
        ("OT", "Other"),
        ("SE", "Securities"),
        ("CH", "Cooperative Housing")
    ]

    EMAIL_FRAMEWORK = """
                Include a succinct statement regarding the financial ask, and a brief description of the property type (e.g., commercial, residential, mixed-use) and location.
                Unique Selling Point: Highlight what makes this property a good investment (e.g., location, high rental demand).

                Detail the property's major features such as square footage, occupancy rates, and unique amenities.
                Strategic Location: Locatedd from [notable landmark or area, e.g., downtown], and from [another key landmark, e.g., a major university hospital]. This prime positioning ensures high visibility/accessibility, benefiting from [mention any specific advantages, e.g., heavy foot traffic, proximity to business hubs, etc.].
                Financials: Provide a snapshot of financial details, including projected ROI and other relevant financial metrics.
                Market Trends: Include insights on market trends, supported by visual comps, to underline the investment potential in the context of current and forecasted market conditions.

                Briefly outline the borrower's experience in this specific property type, highlighting any notable successes or key projects.
                Financial Stability: Mention the borrower's financial strength and stability, supported by relevant metrics or achievements.
                Reputation: Summarize any industry recognitions, awards, or testimonials that underscore the borrower's reputation in the market.

                Encourage the lender to express interest, pass, or request more detailed information.
                
                The email should be concise and have headers for the different features.

                """
    EMAIL_EXAMPLE = """
We haven't met - but would like to kick off a relationship and trade some of our incoming deal flow. 
 
Currently, we have an exclusive investment opportunity (construction) in a high-potential self-storage project in Morganton, NC, developed in partnership between S3 Partners and MPIG. This venture represents not just a sound investment, but a unique opportunity for a comprehensive financing partnership on future deals with the group.  

Project Overview:
·  Location: Prime 2.13-acre site in Morganton, NC
·  Development: 3-story, climate-controlled self-storage facility
·  Current Progress: Secured senior debt with FNB, alongside substantial project milestones including feasibility study, environmental assessment, and more.
·  Projected Value: Stabilized value estimated at $20.3M
While we have a term sheet in place with First National Bank of North Carolina for senior debt, we are open to discussions with lenders interested in providing a more holistic financial solution - including equity. 
 
Ideally, we seek a partnership that could encompass the entire capital stack, potentially simplifying the financial structure and aligning interests more closely.

Funding Needs:
·  Desired Leverage: $1.2M - $1.5M in subordinate debt
·  Total Project Cost: $14M
·  Exit Strategy: Sale to a REIT within two years, with Cubesmart showing preliminary interest.
Pending interest, we have the full file available - including business plans and market research, appraisals, term sheets, etc. 

Would you like to schedule a call to discuss ?
"""