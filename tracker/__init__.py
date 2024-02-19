
class DOCUMENT_TYPE:
    STATUS_CHOICES = [
        ("not_uploaded", "Not Uploaded"),
        ("pending", "Pending"),
        ("rejected", "Rejected"),
        ("approved", "Approved"),
        ("hidden", "Hidden")
        
    ]

class DOCUMENT:

    STATUS_CHOICES = [
        ("not_uploaded", "Not Uploaded"),
        ("pending", "Pending"),
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
        ("Resume or Bio", "Resume", "Demonstrating experience."),
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
        ("Resume or Bio", "Resume", "Experience in leadership."),

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

    MULTI_FAMILY_DOCS = [
        # Sponsor Documents
        ("Government-issued ID", "SponsorGovID", "Driver's License, Passport, etc. to verify identity of the sponsor."),
        ("Personal Financial Statement", "SponsorFinancialStatement", "A document showing sponsor's net worth and liquidity."),
        ("Resume or Bio", "Resume", "Highlighting real estate experience to demonstrate capability and experience."),
        ("Credit Report", "SponsorCreditReport", "Credit history and score of the sponsor for financial reliability assessment."),
        ("Bank Statements", "BankStatements", "To verify cash reserves and financial stability of the sponsor."),
        ("Asset Verification", "AssetVerification", "Documentation of retirement accounts, stocks, etc. for wealth verification."),
        ("Liability Information", "LiabilityInfo", "Existing loans, alimony payments, etc. to assess financial obligations."),
        
        # Property Information
        ("Property Address and Description", "PropertyDescription", "Location details and a comprehensive description of the property."),
        ("Rent Roll", "RentRoll", "Current and comprehensive rent roll to understand income."),
        ("Leases", "Leases", "Copies of all current leases to review terms and tenant commitments."),
        ("Operating Statements (Last 2-3 Years)", "OperatingStatements", "Financial performance records to assess profitability."),
        ("Year-to-Date Operating Statement", "YTDOperatingStatement", "Most recent financial performance assessment."),
        ("Property Tax Statements", "TaxStatements", "To understand property tax obligations."),
        ("Insurance Coverage Details", "InsuranceDetails", "Current insurance coverage specifics."),
        ("Capital Improvements Records", "CapitalImprovements", "Recent renovations or upgrades documentation."),
        
        # Loan Information
        ("Existing Mortgage Details", "MortgageDetails", "Information on current loan terms and balances."),
        ("Refinance Purpose", "RefinancePurpose", "The objective behind the refinance."),
        ("Desired Loan Amount", "LoanAmount", "The amount of funding being requested."),
        
        # Legal Documents
        ("Title Report", "TitleReport", "Shows ownership and any liens on the property."),
        ("Property Deed", "PropertyDeed", "Legal document proving ownership."),
        ("LLC or Partnership Documents", "LLCPartnershipDocs", "If applicable, to show legal business structure."),
        
        # Property Management Information
        ("Property Management Agreement", "ManagementAgreement", "Details of the agreement if managed by a third party."),
        ("Property Management Performance", "ManagementPerformance", "Track record of the property management company."),
        
        # Utility and Maintenance Expenses
        ("Utility Expenses Records", "UtilityExpenses", "Detailed utility expenditure records."),
        ("Maintenance Costs Records", "MaintenanceCosts", "Documentation of maintenance expenses."),
        
        # Amenities and Additional Features
        ("Amenities Operational Costs", "AmenitiesCosts", "Costs associated with maintaining property amenities like pool, gym."),
        
        # Compliance and Regulatory Documents
        ("Affordable Housing Compliance Documents", "AffordableHousingDocs", "Required for units designated as affordable housing."),
        ("Regulatory Compliance Documents", "RegulatoryDocs", "Any other compliance or regulatory documentation."),
        
        # Market Analysis
        ("Market Analysis Report", "MarketAnalysis", "Analysis of property's position within the local market."),
        
        # Additional Documents
        ("Legal Issues Information", "LegalIssues", "Details on any ongoing or past legal issues."),
        ("Other Stakeholders Information", "StakeholdersInfo", "Information on other involved parties, if applicable.")
    ]
