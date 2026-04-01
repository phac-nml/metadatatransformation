process WRITE_METADATA {
    tag "write metadata"
    label 'process_single'

    input:
    val metadata_headers
    val metadata_rows

    output:
    path("results.json"), emit: results

    exec:
    def columns = metadata_headers
    def index = []
    def data = []

    metadata_rows.each {
        index += it[0]
        data += [it]
    }

    // Note: the "sample" ID is duplicated as both the index and as a metadata.
    // This is because transform.py expects a "sample" metadata column header and indices
    // don't have a column header (in Pandas).
    json_data = [
        "index": index,
        "columns": columns,
        "data": data
    ]

    task.workDir.resolve("results.json").withWriter { writer ->
        json_output = groovy.json.JsonOutput.toJson(json_data)
        writer.write(json_output)
    }
}
