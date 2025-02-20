process TRANSFORM_METADATA {
    tag "Transform metadata"
    label 'process_single'

    // TODO: Is there a more specific container we can use with Python and Pandas?
    container "${ workflow.containerEngine == 'singularity' && !task.ext.singularity_pull_docker_container ?
        'https://depot.galaxyproject.org/singularity/staramr:0.10.0--pyhdfd78af_0':
        'biocontainers/staramr:0.10.0--pyhdfd78af_0' }"

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
