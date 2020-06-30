import concurrent.futures
import flask
import plotly
import json
import plotly.express as px
from google.cloud import bigquery

app = flask.Flask(__name__)
bigquery_client = bigquery.Client()
q_from = "Sydney"
q_to = "Helsinki"
q_ddate = "2021-01-01"


@app.route("/")
def main():

    QUERY =  """
        select distinct route, ddate, ceiling(eur) as eurc, eur, cast(tss as DATE) as tss
        from `yyyaaannn.Explore.QR01`
        where `from` = '{}' and `to` = '{}' and `ddate` = DATE('{}') 
    """

    QUERY = QUERY.format(q_from, q_to, q_ddate)

    query_job = bigquery_client.query(QUERY)

    return flask.redirect(
        flask.url_for(
            "results",
            project_id=query_job.project,
            job_id=query_job.job_id,
            location=query_job.location,
        )
    )


@app.route("/results")
def results():
    project_id = flask.request.args.get("project_id")
    job_id = flask.request.args.get("job_id")
    location = flask.request.args.get("location")

    query_job = bigquery_client.get_job(
        job_id,
        project=project_id,
        location=location,
    )

    try:
        df = query_job.result(timeout=20).to_dataframe()
    except concurrent.futures.TimeoutError:
        return flask.render_template("timeout.html", job_id=query_job.job_id)

    fig = px.bar(df, x='tss', y='eur', color='route', barmode='group')
    fig.update_layout(
        title="{} -> {} on {}<br>hover for details|double click to filter routes".format(q_from, q_to, q_ddate),
        xaxis_title=None,
        yaxis_title="EUR"
    )
    
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    return flask.render_template("result.html", plot=graphJSON)


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8080, debug=True)
