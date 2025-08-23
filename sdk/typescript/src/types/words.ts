
export type WordsListResponseData = Word[];
export interface WordsListRequestParams {
    ayah_uuid?: string;
    limit?: number;
    offset?: number;
    ordering?: string;
    search?: string;
}
export interface WordsCreateRequestData {
    ayah_uuid: string;
    text: string;
    uuid: string;
}
export interface WordsCreateResponseData {
    ayah_uuid: string;
    text: string;
    uuid: string;
}
export interface WordsCreateRequestParams {
    ayah_uuid?: string;
}
export interface WordsRetrieveResponseData {
    ayah_uuid: string;
    text: string;
    uuid: string;
}
export interface WordsUpdateRequestData {
    ayah_uuid: string;
    text: string;
    uuid: string;
}
export interface WordsUpdateResponseData {
    ayah_uuid: string;
    text: string;
    uuid: string;
}
export interface WordsPartialupdateRequestData {
    ayah_uuid?: string;
    text?: string;
    uuid?: string;
}
export interface WordsPartialupdateResponseData {
    ayah_uuid: string;
    text: string;
    uuid: string;
}


export interface Word {
    uuid: string;
    text: string;
    ayah_uuid: string;
}