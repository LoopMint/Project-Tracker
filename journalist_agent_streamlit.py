"""Streamlit UI for Journalist Newsworthiness Agent."""

import streamlit as st
from journalist_newsworthiness_agent import (
    JournalistNewsworthinessAgent,
    NewsworthinessTier
)
import plotly.graph_objects as go
import json


def create_score_gauge(score: float, label: str) -> go.Figure:
    """Create a gauge chart for score visualization."""
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score,
        title={'text': label},
        domain={'x': [0, 1], 'y': [0, 1]},
        gauge={
            'axis': {'range': [0, 10]},
            'bar': {'color': "darkblue"},
            'steps': [
                {'range': [0, 3], 'color': "lightgray"},
                {'range': [3, 5], 'color': "gray"},
                {'range': [5, 7], 'color': "lightgreen"},
                {'range': [7, 10], 'color': "green"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 6.5
            }
        }
    ))
    return fig


def create_radar_chart(scores) -> go.Figure:
    """Create radar chart of scoring criteria."""
    categories = [
        'Timeliness',
        'Impact',
        'Novelty',
        'Controversy',
        'SG Relevance',
        'Human Interest',
        'Credibility',
        'Clarity'
    ]
    
    values = [
        scores.timeliness,
        scores.impact,
        scores.novelty,
        scores.controversy,
        scores.sg_relevance,
        scores.human_interest,
        scores.credibility,
        scores.clarity
    ]
    
    fig = go.Figure(data=go.Scatterpolar(
        r=values,
        theta=categories,
        fill='toself'
    ))
    
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 10])),
        title="Newsworthiness Criteria Breakdown"
    )
    
    return fig


def tier_to_color(tier: NewsworthinessTier) -> str:
    """Map tier to color."""
    tier_colors = {
        NewsworthinessTier.HIGHLY_NEWSWORTHY: "🟢",
        NewsworthinessTier.NEWSWORTHY: "🟢",
        NewsworthinessTier.MODERATELY_NEWSWORTHY: "🟡",
        NewsworthinessTier.LOW_NEWSWORTHINESS: "🟠",
        NewsworthinessTier.NOT_NEWSWORTHY: "🔴"
    }
    return tier_colors.get(tier, "⚪")


def main():
    """Main Streamlit app."""
    st.set_page_config(
        page_title="Journalist Newsworthiness Agent",
        page_icon="📰",
        layout="wide"
    )
    
    st.title("📰 Journalist Newsworthiness Agent")
    st.subheader("Evaluate your press release's likelihood of journalist pickup in Singapore")
    
    # Sidebar for input
    with st.sidebar:
        st.header("📝 Input Press Release")
        press_release = st.text_area(
            "Paste your press release here:",
            height=300,
            placeholder="Enter your full press release text..."
        )
        
        analyze_button = st.button("🔍 Analyze Press Release", use_container_width=True)
    
    if analyze_button and press_release:
        with st.spinner("🔄 Analyzing press release..."):
            agent = JournalistNewsworthinessAgent()
            report = agent.evaluate_press_release(press_release)
        
        # Overall Score Section
        col1, col2, col3 = st.columns([1, 1, 1])
        
        with col1:
            st.metric(
                "Overall Newsworthiness Score",
                f"{report.overall_score}/10",
                delta=None
            )
        
        with col2:
            tier_emoji = tier_to_color(report.tier)
            st.metric(
                "Classification",
                f"{tier_emoji} {report.tier.value.replace('_', ' ').title()}"
            )
        
        with col3:
            primary_count = len(report.primary_platforms)
            st.metric(
                "Target Platforms",
                f"{primary_count} Primary"
            )
        
        st.divider()
        
        # Scoring Breakdown
        st.header("📊 Scoring Breakdown")
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig_gauge = create_score_gauge(report.overall_score, "Overall Score")
            st.plotly_chart(fig_gauge, use_container_width=True)
        
        with col2:
            fig_radar = create_radar_chart(report.scoring_breakdown)
            st.plotly_chart(fig_radar, use_container_width=True)
        
        # Detailed scores
        st.subheader("Detailed Criteria Scores")
        scores_df = {
            'Criterion': [
                'Timeliness',
                'Impact',
                'Novelty',
                'Controversy',
                'SG Relevance',
                'Human Interest',
                'Credibility',
                'Clarity'
            ],
            'Score': [
                report.scoring_breakdown.timeliness,
                report.scoring_breakdown.impact,
                report.scoring_breakdown.novelty,
                report.scoring_breakdown.controversy,
                report.scoring_breakdown.sg_relevance,
                report.scoring_breakdown.human_interest,
                report.scoring_breakdown.credibility,
                report.scoring_breakdown.clarity
            ]
        }
        
        st.dataframe(scores_df, use_container_width=True)
        
        st.divider()
        
        # Platform Recommendations
        st.header("🏢 Platform Recommendations")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Primary Target Platforms")
            for platform in report.primary_platforms:
                platform_name = platform.value.replace('_', ' ').title()
                reach = report.estimated_reach.get(platform.value, "N/A")
                st.success(f"✅ {platform_name} ({reach})")
        
        with col2:
            st.subheader("Secondary Target Platforms")
            for platform in report.secondary_platforms:
                platform_name = platform.value.replace('_', ' ').title()
                reach = report.estimated_reach.get(platform.value, "N/A")
                st.info(f"ℹ️ {platform_name} ({reach})")
        
        st.divider()
        
        # Key Story Angles
        st.header("💡 Key Story Angles")
        st.write("Present these angles to journalists for maximum appeal:")
        for i, angle in enumerate(report.key_angles, 1):
            st.write(f"{i}. **{angle}**")
        
        st.divider()
        
        # Journalist Targeting
        st.header("👥 Journalist Targeting Recommendations")
        st.write("Target these types of journalists at your platform of choice:")
        
        for platform, journalist_types in report.journalist_targeting.items():
            if report.primary_platforms + report.secondary_platforms:
                platform_matches = [p.value for p in report.primary_platforms + report.secondary_platforms]
                if platform in platform_matches:
                    platform_name = platform.replace('_', ' ').title()
                    st.subheader(platform_name)
                    for j_type in journalist_types:
                        st.write(f"• {j_type}")
        
        st.divider()
        
        # Improvement Suggestions
        st.header("📈 Improvement Suggestions")
        
        if report.improvements:
            for i, improvement in enumerate(report.improvements, 1):
                with st.expander(f"**{i}. {improvement.category.title()}** (Priority: {improvement.priority.upper()})"):
                    st.write(f"**Current Score:** {improvement.current_score}/10")
                    st.write(f"**Recommendation:** {improvement.recommendation}")
                    st.write(f"**Example:** {improvement.example}")
        else:
            st.success("✨ No major improvements suggested. Press release is well-optimized!")
        
        st.divider()
        
        # Executive Summary
        st.header("📋 Executive Summary")
        st.write(report.summary)
        
        # Export options
        st.divider()
        st.header("💾 Export Report")
        
        col1, col2 = st.columns(2)
        
        with col1:
            report_json = {
                'overall_score': report.overall_score,
                'tier': report.tier.value,
                'primary_platforms': [p.value for p in report.primary_platforms],
                'secondary_platforms': [p.value for p in report.secondary_platforms],
                'improvements': [
                    {
                        'category': imp.category,
                        'current_score': imp.current_score,
                        'recommendation': imp.recommendation,
                        'priority': imp.priority
                    }
                    for imp in report.improvements
                ]
            }
            
            st.download_button(
                "📥 Download JSON Report",
                json.dumps(report_json, indent=2),
                "newsworthiness_report.json",
                "application/json"
            )
        
        with col2:
            csv_data = "Criterion,Score\n"
            csv_data += f"Timeliness,{report.scoring_breakdown.timeliness}\n"
            csv_data += f"Impact,{report.scoring_breakdown.impact}\n"
            csv_data += f"Novelty,{report.scoring_breakdown.novelty}\n"
            csv_data += f"Controversy,{report.scoring_breakdown.controversy}\n"
            csv_data += f"SG Relevance,{report.scoring_breakdown.sg_relevance}\n"
            csv_data += f"Human Interest,{report.scoring_breakdown.human_interest}\n"
            csv_data += f"Credibility,{report.scoring_breakdown.credibility}\n"
            csv_data += f"Clarity,{report.scoring_breakdown.clarity}\n"
            
            st.download_button(
                "📊 Download CSV Scores",
                csv_data,
                "newsworthiness_scores.csv",
                "text/csv"
            )
    
    elif analyze_button and not press_release:
        st.error("⚠️ Please paste a press release to analyze.")
    
    # Footer
    st.divider()
    st.markdown(
        """
        ---
        **About this tool:**
        
        The Journalist Newsworthiness Agent evaluates press releases for likelihood of pickup
        by journalists at Singapore's mainstream and alternative media platforms.
        
        It scores across 8 key criteria and provides specific recommendations to improve
        your press release's chances of coverage.
        
        **Scoring Criteria:**
        - **Timeliness:** Is this happening now?
        - **Impact:** How many people/businesses are affected?
        - **Novelty:** Is this unique/new?
        - **Controversy:** Does it touch on contentious issues?
        - **SG Relevance:** How relevant to Singapore?
        - **Human Interest:** Does it resonate emotionally?
        - **Credibility:** Is the source credible?
        - **Clarity:** Is the message clear?
        """
    )


if __name__ == "__main__":
    main()
