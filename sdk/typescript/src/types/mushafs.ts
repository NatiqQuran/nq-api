
export interface MushafsImportResponseData {
    name: string;
    short_name: string;
    source?: string;
    status?: 'draft' | 'pending_review' | 'published';
    uuid: string;
}
export interface MushafsListResponseData {
    count: number;
    next?: string;
    previous?: string;
    results: object[];
}
export interface MushafsListRequestParams {
    limit?: number;
    offset?: number;
    ordering?: string;
    search?: string;
}
export interface MushafsCreateRequestData {
    name: string;
    short_name: string;
    source?: string;
    status?: 'draft' | 'pending_review' | 'published';
    uuid: string;
}
export interface MushafsCreateResponseData {
    name: string;
    short_name: string;
    source?: string;
    status?: 'draft' | 'pending_review' | 'published';
    uuid: string;
}
export interface MushafsRetrieveResponseData {
    name: string;
    short_name: string;
    source?: string;
    status?: 'draft' | 'pending_review' | 'published';
    uuid: string;
}
export interface MushafsUpdateRequestData {
    name: string;
    short_name: string;
    source?: string;
    status?: 'draft' | 'pending_review' | 'published';
    uuid: string;
}
export interface MushafsUpdateResponseData {
    name: string;
    short_name: string;
    source?: string;
    status?: 'draft' | 'pending_review' | 'published';
    uuid: string;
}
export interface MushafsPartialupdateRequestData {
    name?: string;
    short_name?: string;
    source?: string;
    status?: 'draft' | 'pending_review' | 'published';
    uuid?: string;
}
export interface MushafsPartialupdateResponseData {
    name: string;
    short_name: string;
    source?: string;
    status?: 'draft' | 'pending_review' | 'published';
    uuid: string;
}