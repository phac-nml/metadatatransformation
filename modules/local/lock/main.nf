process LOCK_METADATA {
    tag "Lock metadata"
    label 'process_single'

    input:
    val metadata_headers
    val metadata_rows

    output:
    path("transformation.csv"), emit: transformation  // Machine
    path("results.csv"),        emit: results         // Human

    exec:
    // Machine-readable:
    // We need to slice out the "sample_name" column.
    SAMPLE_NAME_INDEX = 1
    end = metadata_headers.size() - 1

    task.workDir.resolve("transformation.csv").withWriter { writer ->
        // Header:
        header = metadata_headers[0..SAMPLE_NAME_INDEX-1] + metadata_headers[SAMPLE_NAME_INDEX+1..end]
        writer.writeLine(header.join(","))

        // Contents:
        metadata_rows.each {
            row = it[0..SAMPLE_NAME_INDEX-1] + it[SAMPLE_NAME_INDEX+1..end]
            writer.writeLine(row.join(","))
        }
    }

    // Human-readable:
    task.workDir.resolve("results.csv").withWriter { writer ->
        // Header:
        writer.writeLine(metadata_headers.join(","))

        // Contents:
        metadata_rows.each {
            writer.writeLine(it.join(","))
        }
    }
}
