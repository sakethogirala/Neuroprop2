
class DOCUMENT_TYPE:
    STATUS_CHOICES = [
        ("not_uploaded", "Not Uploaded"),
        ("pending", "Pending"),
        ("approved", "Approved"),
        
    ]


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
        # Financial Documents
        ("Financial Statements (Last 2-3 Years)", "FinancialStatements", "Assess financial health, including income, expenses, and net profit."),
        ("Rent Roll", "RentRoll", "Detailed tenant lease terms and rent amounts."),
        ("Current Year Budget", "CurrentYearBudget", "Forecasted revenue and expenses."),
        ("Bank Statements (Last 3-6 Months)", "BankStatements", "Verify financial standing and cash flow."),
        ("Debt Service Coverage Ratio (DSCR) Analysis", "DSCRAnalysis", "Evaluate ability to cover loan payments."),

        # Property Documents
        ("Property Appraisal Report", "PropertyAppraisal", "Current valuation."),
        ("Property Insurance Policies", "InsurancePolicies", "Detail coverage."),
        ("Physical Condition Report", "PhysicalCondition", "Assess physical state."),
        ("Environmental Reports", "EnvironmentalReport", "Environmental compliance."),

        # Sponsor Documents
        ("Personal Financial Statement", "PersonalFinancialStatement", "Sponsor's net worth and liquidity."),
        ("Credit Report", "CreditReport", "Credit history and score."),
        ("Resume or Bio", "Resume", "Experience in self-storage/related industries."),

        # Legal and Compliance Documents
        ("Title Report", "TitleReport", "Ownership and liens."),
        ("Zoning and Compliance Certifications", "ZoningCompliance", "Regulatory compliance."),
        ("Operating Licenses and Permits", "OperatingLicenses", "Legal operation proof."),

        # Additional Supporting Documents
        ("Capital Improvement Records", "CapitalImprovements", "Document renovations/improvements."),
        ("Market Analysis Reports", "MarketAnalysis", "Market conditions and competition."),
        ("Lease Abstracts", "LeaseAbstracts", "Summary of key lease terms."),
        ("Management Agreements", "ManagementAgreements", "Details of facility management.")
    ]
