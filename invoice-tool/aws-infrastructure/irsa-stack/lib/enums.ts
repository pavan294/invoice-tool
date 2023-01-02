
export enum AwsAccount {
    Dev = '533000593978',
    Prod = '709002721800',
}

export enum AwsRegion {
    Dev = 'eu-central-1',
    Prod = 'eu-central-1',
}

export enum AwsContext {
    Dev = 'devops-k8s-newvpc',
    Prod = 'devops-k8s-newvpc',
}

export enum K8sNamespace {
    Dev = 'backoffice-dev',
    Prod = 'backoffice'
}

export enum K8sServiceAccountApi {
    Dev = 'nordpool-invoice-downloader-api',
    Prod = 'nordpool-invoice-downloader-api'
}

export enum K8sServiceAccountCronJob {
    Dev = 'nordpool-invoice-downloader-cronjob',
    Prod = 'nordpool-invoice-downloader-cronjob'
}