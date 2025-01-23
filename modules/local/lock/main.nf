process LOCK_METADATA {
    tag "Locks metadata"
    label 'process_single'

    input:
    val input
    
    output:
    path("locked.csv"), emit: locked

    exec:
    task.workDir.resolve("locked.csv").withWriter { writer ->
        // Header:
        writer.writeLine("column1,column2,column3")

        // Contents:
        input.each {
            name = it[0].id
            metadata = it[1]
            line = ([name] + metadata).join(",")
            writer.writeLine(line)
        }
    }
}