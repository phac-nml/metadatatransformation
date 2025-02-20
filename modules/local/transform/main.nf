process TRANSFORM_METADATA {
    tag "Transform metadata"
    label 'process_single'

    container "${ workflow.containerEngine == 'singularity' && !task.ext.singularity_pull_docker_container ?
        'https://depot.galaxyproject.org/singularity/python:3.8.3' :
        'biocontainers/python:3.8.3' }"

    input:
    path metadata
    val transformation

    output:
    path("transformation.csv"), emit: transformation  // Machine-readable
    path("results.csv"),        emit: results         // Human-readable
    path("versions.yml"),       emit: versions

    script:
    """
    transform.py ${metadata} ${transformation}

    cat <<-END_VERSIONS > versions.yml
    "${task.process}":
        python: \$(python --version | sed 's/Python //g')
    END_VERSIONS
    """
}
