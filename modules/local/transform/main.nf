process TRANSFORM_METADATA {
    tag "transform metadata"
    label 'process_single'

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
    def args = task.ext.args ?: ''

    """
    transform.py ${metadata} ${transformation} $args

    cat <<-END_VERSIONS > versions.yml
    "${task.process}":
        python: \$(python --version | sed 's/Python //g')
    END_VERSIONS
    """
}
