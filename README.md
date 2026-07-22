# Iran Job Market Intelligence Platform

## Turning Raw Job Data into Market Intelligence & Personalized Recommendations

An end-to-end data analytics and machine learning platform designed to analyze the Iranian job market, discover high-demand skills, understand salary trends, extract business insights, and provide personalized job recommendations.

Unlike projects based on ready-made datasets, this project started from raw web data collection and developed into a complete data product through:

- Web Scraping
- Data Engineering
- Data Cleaning
- Data Quality Validation
- Exploratory Data Analysis
- Feature Engineering
- NLP-Based Recommendation System
- Interactive Dashboard

---

# Project Overview

The job market generates thousands of job advertisements every day, but most of this information remains unstructured and difficult to analyze.

This project transforms raw job advertisements into actionable intelligence by answering questions such as:

- Which skills are most demanded in the market?
- Which technologies provide better career opportunities?
- How does salary vary based on skills, experience, and location?
- Which companies and industries are actively hiring?
- What skills should candidates learn to improve their opportunities?
- Which jobs are the best match for a candidate profile?

The final goal is to build a data-driven job market intelligence platform.

---

# End-to-End Project Workflow

```
Job Platform Data
        |
        ↓
Web Scraping Pipeline
        |
        ↓
Raw Data Collection
        |
        ↓
Data Cleaning
        |
        ↓
Data Quality Validation
        |
        ↓
Exploratory Data Analysis
        |
        ↓
Feature Engineering
        |
        ↓
Skill & Market Intelligence
        |
        ↓
Recommendation System
        |
        ↓
Interactive Dashboard
        |
        ↓
Business Insights & Recommendations
```

---

# 1. Data Collection & Web Scraping

## Building a Real-World Dataset

Instead of using a pre-cleaned public dataset, this project started by collecting raw job market data directly from:

## JobVision.ir

JobVision is one of the largest Iranian employment platforms, containing thousands of job advertisements across different industries, companies, locations, and career levels.

A custom web scraping pipeline was developed to collect real-world job advertisement data.

Collected information includes:

- Job title
- Company name
- Province
- City
- Salary information
- Employment type
- Remote opportunities
- Internship availability
- Required experience
- Seniority level
- Job category
- Industry
- Company size
- Benefits
- Required skills
- Job description

---

# 2. Data Extraction & Parsing

The collected information was initially unstructured web data.

A data extraction pipeline was developed to transform raw website content into structured datasets.

Main tasks:

- HTML parsing
- Extracting required fields
- Converting nested information into columns
- Cleaning extracted text
- Handling missing elements
- Preparing datasets for analysis

---

# 3. Data Storage & Organization

The project follows a structured data workflow:

```
data/

├── raw/
│     └── Original scraped data
│
└── processed/
      └── Clean analytical datasets
```

Raw data was preserved separately from processed data to maintain reproducibility and support future improvements.

---

# 4. Data Cleaning & Preprocessing

Real-world scraped data contains noise, inconsistencies, and missing information.

A complete preprocessing pipeline was implemented.

Performed tasks:

- Removing duplicate advertisements
- Handling missing values
- Fixing incorrect data types
- Standardizing categories
- Persian text normalization
- Skill normalization
- Salary preprocessing
- Extracting structured information from descriptions

Example:

Before:

```
python
Python
PYTHON
```

After:

```
Python
```

---

# 5. Data Quality Validation

Before performing analytics, the dataset quality was evaluated.

Validation checks included:

- Missing value analysis
- Duplicate detection
- Invalid salary ranges
- Incorrect experience values
- Inconsistent categories
- Empty critical fields
- Data integrity validation

The goal was to create a reliable analytical dataset instead of directly analyzing noisy scraped data.

---

# 6. Exploratory Data Analysis (EDA)

A complete EDA process was performed to understand the Iranian job market.

## Market Overview Analysis

Analyzed:

- Total job advertisements
- Hiring activity by province
- Popular cities
- Active companies
- Job categories
- Employment types

Business questions:

- Where is hiring concentrated?
- Which industries have higher demand?
- Which roles are most common?

---

## Salary Intelligence

Analyzed:

- Salary distribution
- Salary ranges
- Experience vs salary relationship
- Salary differences between roles
- Location-based salary variations

Business questions:

- Which jobs have higher earning potential?
- How much does experience affect salary?
- Which skills are associated with higher compensation?

---

## Skill Demand Analysis

Job descriptions were analyzed to identify market demand.

Extracted insights:

- Most demanded technical skills
- Programming languages
- Data tools
- Frameworks
- Technology combinations

Examples:

- Python
- SQL
- Excel
- Power BI
- Data Analysis
- Machine Learning

---

# 7. Feature Engineering

New analytical features were created to support deeper analysis and machine learning.

Created features:

- Skill count per job
- Extracted technology tags
- Salary bands
- Experience groups
- Seniority groups
- Location indicators
- Job complexity indicators

These features transformed raw advertisements into meaningful analytical variables.

---

# 8. Market Intelligence & Business Analysis

After preparing the data, business-focused analysis was performed.

The project investigates:

- Current market trends
- Most valuable skills
- Hiring patterns
- Career opportunities
- Skill gaps
- Company hiring behavior

The objective is converting raw job advertisements into actionable insights.

---

# 9. Recommendation System

## Building an Intelligent Job Matching Engine

The final stage of the project was developing a recommendation system to match candidates with suitable job opportunities.

The system answers:

> Given a candidate's skills and experience, which jobs are the most relevant?

---

## Recommendation Approach

A content-based filtering approach was implemented.

The system compares:

```
Candidate Profile

        ↔

Job Requirements
```

Based on:

- Candidate skills
- Required skills
- Experience level
- Job category
- Technical requirements

---

# Text Processing & Feature Representation

Because job descriptions and skills are text-based, they were converted into numerical vectors.

Pipeline:

```
Raw Skills / Job Description
            |
            ↓
    Text Preprocessing
            |
            ↓
    TF-IDF Vectorization
            |
            ↓
 Similarity Calculation
            |
            ↓
 Ranked Recommendations
```

---

# TF-IDF Vectorization

TF-IDF (Term Frequency - Inverse Document Frequency) was used to measure the importance of skills inside job descriptions.

Formula:

```
TF-IDF(t,d) = TF(t,d) × IDF(t)
```

## Term Frequency

```
TF(t,d) =
Number of times term appears in document
/
Total number of terms in document
```

## Inverse Document Frequency

```
IDF(t) =
log(
Total Documents
/
Documents containing term
)
```

This allows the model to identify more meaningful technical skills.

---

# Similarity Calculation

After vectorization, candidate profiles and jobs were compared using Cosine Similarity.

Formula:

```
Cosine Similarity(A,B)

        A · B
--------------------
      ||A|| × ||B||
```

Where:

- A = Candidate vector
- B = Job vector

Similarity score:

```
0 → No similarity

1 → Perfect match
```

---

# Recommendation Pipeline

```
Candidate Skills

      ↓

Create Candidate Vector

      ↓

Compare With All Jobs

      ↓

Calculate Similarity Score

      ↓

Sort Results

      ↓

Return Top-N Recommendations
```

---

# Custom Recommendation Functions

Reusable functions were created for:

- Processing candidate skills
- Creating feature vectors
- Calculating similarity scores
- Ranking jobs
- Returning top recommendations

Example:

```python
recommend_jobs(
    candidate_skills,
    top_n=10
)
```

---

# Recommendation Challenges

## Skill Normalization

Different formats:

```
python
Python
PYTHON
```

were standardized into:

```
Python
```

---

## Missing Skills

Solutions:

- Extracting keywords from descriptions
- Using multiple text fields
- Combining skill information

---

## Persian Text Processing

Handled:

- Persian character normalization
- Text cleaning
- Noise removal
- Skill standardization

---

# 10. Interactive Dashboard

The final insights are presented through an interactive dashboard.

Dashboard sections:

## Market Overview

- Total jobs
- Companies
- Locations
- Categories

## Salary Analytics

- Salary trends
- Role comparison
- Experience impact

## Skill Intelligence

- Most demanded skills
- Technology trends

## Recommendation Module

- Candidate-job matching

---

# Business Applications

This platform can support:

- Recruitment analytics
- HR intelligence systems
- Career recommendation platforms
- Workforce planning
- Skill gap analysis

---

# Final Project Outcome

This project demonstrates the complete lifecycle of a real-world data product:

```
Web Scraping
      ↓
Data Engineering
      ↓
Data Cleaning
      ↓
Data Quality
      ↓
Exploratory Analytics
      ↓
Feature Engineering
      ↓
Machine Learning
      ↓
Recommendation System
      ↓
Business Intelligence
```

The final result is an end-to-end Job Market Intelligence Platform built from real-world collected data.

---

# Author

**Behnia Shaygan**

Data Analytics & Data Science Portfolio Project
