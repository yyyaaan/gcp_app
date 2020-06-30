import concurrent.futures
import flask
import plotly
import json
import plotly.express as px
from google.cloud import bigquery

app = flask.Flask(__name__)
bigquery_client = bigquery.Client()
QUERY =  """
  select distinct route, concat(`from`, '>', `to`, ' on ',  FORMAT_DATE("%d%b", ddate)) as flight, ceiling(eur) as eur, cast(tss as DATE) as tss
  from `yyyaaannn.Explore.QR01`
  where (`from` = '{}' and `to` = '{}' and `ddate` = DATE('{}'))
     or (`from` = '{}' and `to` = '{}' and `ddate` = DATE('{}'))
"""


@app.route("/")
def main():

    q_route = flask.request.args.get("q_route")
    q_ddate = flask.request.args.get("q_ddate")
    q_rdate = flask.request.args.get("q_rdate")

    # override if empty
    if q_ddate is None: q_ddate = "2021-01-01"
    if q_rdate is None: q_rdate = "2021-01-06"
    if q_route is None: q_route = "Helsinki Canberra|Sydney Oslo"

    q_dests = q_route.replace("|", " ").split(" ")

    query_job = bigquery_client.query(QUERY.format(q_dests[0], q_dests[1], q_ddate, q_dests[2], q_dests[3], q_rdate))

    return flask.redirect(
        flask.url_for(
            "results",
            text=q_route + q_ddate + q_rdate,
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

    query_job = bigquery_client.get_job(job_id, project=project_id, location=location,)

    try:
        df = query_job.result(timeout=20).to_dataframe()
    except concurrent.futures.TimeoutError:
        return flask.render_template("timeout.html", job_id=query_job.job_id)

    fig = px.bar(df, x='tss', y='eur', color='route', barmode='group', facet_row='flight', height=900)
    
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    return flask.render_template("result.html", plot=graphJSON, text= flask.request.args.get("text"))


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8080, debug=True)
