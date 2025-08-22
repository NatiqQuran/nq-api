import * as PhrasesType from "../types/phrases";
import { AxiosResponse } from "axios";
import { Connection } from "../client/connection";
import { BaseController } from "../utils/baseController";
import { RequestConfig } from "../utils/globalTypes";

export class PhrasesModify extends BaseController {
    constructor(conn: Connection, token?: string) {
        super(conn, token);
    }
    /** POST /phrases/modify/ */
    async phrases_modify_create(data: PhrasesType.PhrasesModifyPostRequestData, config?: RequestConfig<PhrasesType.PhrasesModifyRequestParams>
    ): Promise<AxiosResponse<PhrasesType.PhrasesModifyPostResponseData>> {
        return await this.axiosPost(`/phrases/modify/`, data, config);
    }
}

export class PhrasesController extends BaseController {
    public readonly modify: PhrasesModify;

    constructor(connection: Connection, token?: string) {
        super(connection, token);
        this.modify = new PhrasesModify(this.conn);
    }
    
    /** GET /phrases/ */
    async list(config?: RequestConfig
    ): Promise<AxiosResponse<PhrasesType.PhrasesListResponseData>> {
        return await this.axiosGet(`/phrases/`, config);
    }
    
    /** POST /phrases/ */
    async create(data: PhrasesType.PhrasesCreateRequestData, config?: RequestConfig
    ): Promise<AxiosResponse<PhrasesType.PhrasesCreateResponseData>> {
        return await this.axiosPost(`/phrases/`, data, config);
    }
    
    /** GET /phrases/{uuid}/ */
    async retrieve(uuid: string, config?: RequestConfig
    ): Promise<AxiosResponse<PhrasesType.PhrasesRetrieveResponseData>> {
        return await this.axiosGet(`/phrases/${uuid}/`, config);
    }
    
    /** PUT /phrases/{uuid}/ */
    async update(uuid: string, data: PhrasesType.PhrasesUpdateRequestData, config?: RequestConfig
    ): Promise<AxiosResponse<PhrasesType.PhrasesUpdateResponseData>> {
        return await this.axiosPut(`/phrases/${uuid}/`, data, config);
    }
    
    /** PATCH /phrases/{uuid}/ */
    async partialUpdate(uuid: string, data: PhrasesType.PhrasesPartialupdateRequestData, config?: RequestConfig
    ): Promise<AxiosResponse<PhrasesType.PhrasesPartialupdateResponseData>> {
        return await this.axiosPatch(`/phrases/${uuid}/`, data, config);
    }
    
    /** DELETE /phrases/{uuid}/ */
    async delete(uuid: string, config?: RequestConfig
    ): Promise<AxiosResponse<any>> {
        return await this.axiosDelete(`/phrases/${uuid}/`, config);
    }
    
}