
class DOCUMENT:

    STATUS_CHOICES = [
        ("not_uploaded", "Not Uploaded"),
        ("pending", "Pending"),
        ("revising", "Revising"),
        ("approved", "Approved"),
        ("rejected", "Rejected")
    ]

    # Name, Type, description
    HOTEL_DOCS = [
        # Financial Docs
        ("Financial Statements (Last 2 - 3 Years)", "FinancialStatements", "Balance Sheets, P&L Statements, Cash Flow Statements to assess financial health."),
        ("T-12 Reports", "T12Reports", "Trailing Twelve Months Financials: Monthly detailed financial reports for recent financial performance."),
        ("Current Year Budget", "CurrentYearBudget", "Detailed revenue and expense budget for current fiscal year."),
        ("Bank Statements (Last 3 - 6 Months)", "BankStatements", "Bank Statements to verify cash reserves and financial stability."),

        # Property Docs
        ("Property Appraisal Report", "PropertyAppraisal", "Recent appraisal of the property for valuation."),
        ("Title Report", "TitleReport", "Shows ownership and any liens on the property."),
        ("Property Insurance Policies", "InsurancePolicies", "Detailing coverage specifics of the property insurance."),
        ("STR Reports", "STRReport", "Competitive set analysis and market benchmarking."),

        # Sponsor Documents
        ("Personal Financial Statement", "SponsorFinancialStatement", "Net worth and liquidity of the sponsor."),
        ("Credit Report", "SponsorCreditReport", "Credit history and score of the sponsor."),
        ("Resume or Bio", "SponsorResume", "Demonstrating experience."),
        ("Tax Returns (Last 2-3 Years)", "TaxReturns", "Personal and business tax documents for financial assessment."),

        # Legal and Compliance Documents
        ("Franchise Agreement (If Applicable)", "FranchiseAgreement", "Agreements with hotel brands like Marriott, Hilton, etc."),
        ("Zoning and Compliance Certifications", "ZoningCompliance", "Ensuring the property meets all local regulations."),

        # Additional Supporting Documents
        ("Capital Improvement Records", "CapitalImprovements", "Details of recent and planned improvements."),
        ("Market Analysis Reports", "MarketAnalysis", "Assessing market conditions and hotel's position."),
        ("Lease Agreements (If Applicable)", "LeaseAgreements", "For any leased space within the hotel.")
    ]

    SELF_STORAGE_DOCS = [
        ("doc-1", "FILENAME"),
        ("doc-2", "FILENAME2"),
    ]