process LOCK_METADATA {
    tag "Locks metadata"
    label 'process_single'

    input:
    val metadata_headers
    val metadata_rows
    
    output:
    path("locked.csv"), emit: locked

    exec:
    task.workDir.resolve("locked.csv").withWriter { writer ->
        // Header:
        writer.writeLine(metadata_headers.join(","))

        // Contents:
        metadata_rows.each {
            writer.writeLine(it.join(","))
        }
    }
}
