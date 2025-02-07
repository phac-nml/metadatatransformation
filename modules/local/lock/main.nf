process LOCK_METADATA {
    tag "Lock metadata"
    label 'process_single'

    input:
    val metadata_headers
    val metadata_rows

    output:
    path("transformation.csv"), emit: locked

    exec:
    task.workDir.resolve("transformation.csv").withWriter { writer ->
        // Header:
        writer.writeLine(metadata_headers.join(","))

        // Contents:
        metadata_rows.each {
            writer.writeLine(it.join(","))
        }
    }
}
